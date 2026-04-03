from django.utils import timezone
from rest_framework import serializers

from .models import Event, Registration


class RegistrationSerializer(serializers.ModelSerializer):
    participant = serializers.StringRelatedField()

    class Meta:
        model = Registration
        fields = ('id', 'event', 'participant', 'status',
                  'registered_at', 'comment')


class RegistrationCreateSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True,
                                    default='')


class EventListSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    participants_count = serializers.IntegerField(read_only=True)
    available_spots = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'category', 'location', 'event_date',
                  'status', 'created_by', 'participants_count',
                  'available_spots')

    def get_available_spots(self, obj):
        if obj.max_participants == 0:
            return None
        count = (obj.participants_count
                 if isinstance(obj.participants_count, int)
                 else obj.registrations.filter(status='registered').count())
        return max(0, obj.max_participants - count)


class EventDetailSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    registrations = RegistrationSerializer(many=True, read_only=True)
    participants_count = serializers.SerializerMethodField()
    available_spots = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'category', 'location',
                  'event_date', 'max_participants', 'status', 'created_by',
                  'created_at', 'updated_at', 'registrations',
                  'participants_count', 'available_spots')

    def get_participants_count(self, obj):
        return obj.registrations.filter(status='registered').count()

    def get_available_spots(self, obj):
        if obj.max_participants == 0:
            return None
        return max(0, obj.max_participants - self.get_participants_count(obj))


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'category', 'location',
                  'event_date', 'max_participants', 'status')

    def validate_event_date(self, value):
        if not self.instance and value <= timezone.now():
            raise serializers.ValidationError(
                'Дата события должна быть в будущем.')
        return value

    def validate_max_participants(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'Количество участников не может быть отрицательным.')
        return value
