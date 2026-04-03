from django.db.models import Sum
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Contribution, Need
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    ContributionSerializer, NeedListSerializer, NeedSerializer,
)


class NeedViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для нужд приюта.

    list: список всех нужд (доступен всем).
    create: создать нужду (только аутентифицированные).
    retrieve: детали нужды (доступен всем).
    update/partial_update/destroy: только автор.
    """
    queryset = Need.objects.all()
    serializer_class = NeedSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_fields = ('category', 'priority', 'status')
    search_fields = ('title', 'description')
    ordering_fields = ('created_at', 'priority', 'quantity_required')

    def get_serializer_class(self):
        if self.action == 'list':
            return NeedListSerializer
        return NeedSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def _update_need_status(self, need):
        """Автоматически обновляет статус нужды."""
        fulfilled = need.contributions.aggregate(
            total=Sum('quantity'))['total'] or 0
        if fulfilled >= need.quantity_required:
            need.status = 'closed'
        elif fulfilled > 0:
            need.status = 'partially_closed'
        else:
            need.status = 'open'
        need.save()

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def contribute(self, request, pk=None):
        """Внести вклад в закрытие нужды: POST /needs/{id}/contribute/"""
        need = self.get_object()

        if need.status == 'closed':
            return Response(
                {'detail': 'Эта нужда уже полностью закрыта.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ContributionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        fulfilled = need.contributions.aggregate(
            total=Sum('quantity'))['total'] or 0
        remaining = need.quantity_required - fulfilled

        if serializer.validated_data['quantity'] > remaining:
            raise serializers.ValidationError(
                {'quantity': f'Осталось закрыть только {remaining} '
                             f'{need.get_unit_display()}.'}
            )

        serializer.save(contributor=request.user, need=need)
        self._update_need_status(need)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """История вкладов нужды: GET /needs/{id}/history/"""
        need = self.get_object()
        contributions = need.contributions.all()
        serializer = ContributionSerializer(contributions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='urgent')
    def urgent_needs(self, request):
        """Срочные открытые нужды: GET /needs/urgent/"""
        needs = Need.objects.filter(
            priority='urgent',
        ).exclude(status='closed')
        serializer = NeedListSerializer(needs, many=True)
        return Response(serializer.data)


class ContributionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """
    Все вклады (только чтение).
    Создание вкладов — через /needs/{id}/contribute/.
    """
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    filterset_fields = ('need', 'contributor')
    search_fields = ('comment',)
    ordering_fields = ('created_at', 'quantity')
