from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

CATEGORY_CHOICES = (
    ('food', 'Корм'),
    ('medicine', 'Лекарства'),
    ('toys', 'Игрушки'),
    ('equipment', 'Оборудование'),
    ('hygiene', 'Гигиена'),
    ('other', 'Другое'),
)

PRIORITY_CHOICES = (
    ('low', 'Низкий'),
    ('medium', 'Средний'),
    ('high', 'Высокий'),
    ('urgent', 'Срочный'),
)

STATUS_CHOICES = (
    ('open', 'Открыта'),
    ('partially_closed', 'Частично закрыта'),
    ('closed', 'Закрыта'),
)

UNIT_CHOICES = (
    ('pcs', 'шт.'),
    ('kg', 'кг'),
    ('l', 'л'),
    ('pack', 'уп.'),
)


class Need(models.Model):
    """Позиция в wishlist приюта — что нужно котикам."""
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    category = models.CharField(
        'Категория', max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(
        'Приоритет', max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(
        'Статус', max_length=20, choices=STATUS_CHOICES, default='open')
    quantity_required = models.PositiveIntegerField('Сколько нужно')
    unit = models.CharField(
        'Единица измерения', max_length=10, choices=UNIT_CHOICES, default='pcs')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='needs',
        verbose_name='Создал')
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Нужда'
        verbose_name_plural = 'Нужды'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'created_by'],
                name='unique_need_per_user',
            )
        ]

    def __str__(self):
        return self.title


class Contribution(models.Model):
    """Закрытие нужды — кто и сколько внёс."""
    need = models.ForeignKey(
        Need, on_delete=models.CASCADE, related_name='contributions',
        verbose_name='Нужда')
    contributor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='contributions',
        verbose_name='Помощник')
    quantity = models.PositiveIntegerField('Количество')
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Когда', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Вклад'
        verbose_name_plural = 'Вклады'

    def __str__(self):
        return f'{self.contributor} → {self.need}: {self.quantity}'
