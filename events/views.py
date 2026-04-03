from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event, Registration
from .permissions import IsOrganizerOrReadOnly
from .serializers import (
    EventCreateUpdateSerializer,
    EventDetailSerializer,
    EventListSerializer,
    RegistrationCreateSerializer,
    RegistrationSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.annotate(
        participants_count=Count(
            'registrations',
            filter=Q(registrations__status='registered')
        )
    )
    permission_classes = (IsOrganizerOrReadOnly,)
    filterset_fields = ('category', 'status')
    search_fields = ('title', 'description')
    ordering_fields = ('event_date', 'created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return EventCreateUpdateSerializer
        return EventDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def register(self, request, pk=None):
        event = self.get_object()
        if event.status in ('cancelled', 'completed'):
            return Response(
                {'detail': 'Нельзя записаться на отменённое или '
                           'завершённое событие.'},
                status=status.HTTP_400_BAD_REQUEST)

        existing = Registration.objects.filter(
            event=event, participant=request.user).first()
        if existing and existing.status == 'registered':
            return Response(
                {'detail': 'Вы уже записаны на это событие.'},
                status=status.HTTP_400_BAD_REQUEST)

        if (event.max_participants > 0
                and event.participants_count >= event.max_participants):
            return Response(
                {'detail': 'Все места заняты.'},
                status=status.HTTP_400_BAD_REQUEST)

        serializer = RegistrationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if existing and existing.status == 'cancelled':
            existing.status = 'registered'
            existing.comment = serializer.validated_data.get('comment', '')
            existing.save()
            return Response(
                RegistrationSerializer(existing).data,
                status=status.HTTP_201_CREATED)

        reg = Registration.objects.create(
            event=event,
            participant=request.user,
            comment=serializer.validated_data.get('comment', ''))
        return Response(
            RegistrationSerializer(reg).data,
            status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='cancel-registration')
    def cancel_registration(self, request, pk=None):
        event = self.get_object()
        try:
            reg = Registration.objects.get(
                event=event, participant=request.user)
        except Registration.DoesNotExist:
            return Response(
                {'detail': 'Вы не записаны на это событие.'},
                status=status.HTTP_404_NOT_FOUND)

        if reg.status == 'cancelled':
            return Response(
                {'detail': 'Регистрация уже отменена.'},
                status=status.HTTP_400_BAD_REQUEST)

        reg.status = 'cancelled'
        reg.save()
        return Response(RegistrationSerializer(reg).data)

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        event = self.get_object()
        regs = event.registrations.filter(status='registered')
        serializer = RegistrationSerializer(regs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        events = Event.objects.filter(
            status='planned', event_date__gt=timezone.now()
        ).order_by('event_date')
        page = self.paginate_queryset(events)
        if page is not None:
            serializer = EventListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)


class RegistrationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    filterset_fields = ('event', 'participant', 'status')
    ordering_fields = ('registered_at',)
