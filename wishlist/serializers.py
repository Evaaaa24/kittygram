from django.db.models import Sum
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import (
    CATEGORY_CHOICES, PRIORITY_CHOICES, STATUS_CHOICES, UNIT_CHOICES,
    Contribution, Need,
)


class ContributionSerializer(serializers.ModelSerializer):
    """Сериализатор вклада (закрытия нужды)."""
    contributor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Contribution
        fields = ('id', 'contributor', 'quantity', 'comment', 'created_at')
        read_only_fields = ('created_at',)

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Количество должно быть больше нуля.')
        return value


class NeedSerializer(serializers.ModelSerializer):
    """Полный сериализатор нужды (для detail-запросов)."""
    created_by = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    contributions = ContributionSerializer(read_only=True, many=True)
    category = serializers.ChoiceField(choices=CATEGORY_CHOICES)
    priority = serializers.ChoiceField(choices=PRIORITY_CHOICES)
    unit = serializers.ChoiceField(choices=UNIT_CHOICES)
    quantity_fulfilled = serializers.SerializerMethodField()
    quantity_remaining = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Need
        fields = (
            'id', 'title', 'description', 'category', 'priority', 'status',
            'quantity_required', 'unit', 'quantity_fulfilled',
            'quantity_remaining', 'progress', 'created_by', 'created_at',
            'updated_at', 'contributions',
        )
        read_only_fields = ('status', 'created_at', 'updated_at')
        validators = [
            UniqueTogetherValidator(
                queryset=Need.objects.all(),
                fields=('title', 'created_by'),
                message='Вы уже создали нужду с таким названием.',
            )
        ]

    def get_quantity_fulfilled(self, obj):
        result = obj.contributions.aggregate(total=Sum('quantity'))
        return result['total'] or 0

    def get_quantity_remaining(self, obj):
        fulfilled = self.get_quantity_fulfilled(obj)
        remaining = obj.quantity_required - fulfilled
        return max(remaining, 0)

    def get_progress(self, obj):
        if obj.quantity_required == 0:
            return 100
        fulfilled = self.get_quantity_fulfilled(obj)
        return min(round(fulfilled / obj.quantity_required * 100, 1), 100)

    def validate_quantity_required(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Количество должно быть больше нуля.')
        return value


class NeedListSerializer(serializers.ModelSerializer):
    """Краткий сериализатор нужды (для списка)."""
    created_by = serializers.StringRelatedField(read_only=True)
    category = serializers.ChoiceField(choices=CATEGORY_CHOICES)
    priority = serializers.ChoiceField(choices=PRIORITY_CHOICES)
    quantity_fulfilled = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Need
        fields = (
            'id', 'title', 'category', 'priority', 'status',
            'quantity_required', 'quantity_fulfilled', 'unit',
            'progress', 'created_by', 'created_at',
        )

    def get_quantity_fulfilled(self, obj):
        result = obj.contributions.aggregate(total=Sum('quantity'))
        return result['total'] or 0

    def get_progress(self, obj):
        if obj.quantity_required == 0:
            return 100
        fulfilled = self.get_quantity_fulfilled(obj)
        return min(round(fulfilled / obj.quantity_required * 100, 1), 100)
