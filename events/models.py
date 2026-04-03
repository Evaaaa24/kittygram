from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

CATEGORY_CHOICES = (
    ('exhibition', 'Выставка'),
    ('meetup', 'Встреча'),
    ('adoption', 'День усыновления'),
    ('vaccination', 'Вакцинация'),
    ('other', 'Другое'),
)

STATUS_CHOICES = (
    ('planned', 'Запланировано'),
    ('ongoing', 'Проходит'),
    ('completed', 'Завершено'),
    ('cancelled', 'Отменено'),
)

REGISTRATION_STATUS = (
    ('registered', 'Зарегистрирован'),
    ('cancelled', 'Отменён'),
)


class Event(models.Model):
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    category = models.CharField(
        'Категория', max_length=20, choices=CATEGORY_CHOICES)
    location = models.CharField('Место', max_length=300)
    event_date = models.DateTimeField('Дата события')
    max_participants = models.PositiveIntegerField(
        'Макс. участников', default=0,
        help_text='0 = без ограничения')
    status = models.CharField(
        'Статус', max_length=20, choices=STATUS_CHOICES, default='planned')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_events', verbose_name='Организатор')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-event_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'event_date'],
                name='unique_event_title_date'
            )
        ]

    def __str__(self):
        return self.title


class Registration(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE,
        related_name='registrations', verbose_name='Событие')
    participant = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='event_registrations', verbose_name='Участник')
    status = models.CharField(
        'Статус', max_length=20,
        choices=REGISTRATION_STATUS, default='registered')
    registered_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField('Комментарий', blank=True)

    class Meta:
        ordering = ['-registered_at']
        constraints = [
            models.UniqueConstraint(
                fields=['event', 'participant'],
                name='unique_registration'
            )
        ]

    def __str__(self):
        return f'{self.participant} → {self.event}'
