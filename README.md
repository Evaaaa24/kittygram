# Kittygram + Wishlist

## Описание идеи

Kittygram — социальная платформа для хозяев котиков, где можно зарегистрировать своего кота, указать его цвет, год рождения и достижения.

**Wishlist нужд приюта** — расширение для Kittygram, которое позволяет приютам для животных публиковать список того, что им нужно (корм, лекарства, оборудование), а пользователи могут закрывать эти нужды частично или полностью. У каждой нужды отображается прогресс закрытия и история вкладов. Это помогает приютам получать адресную помощь, а волонтёрам — видеть, где их вклад нужен больше всего.

## Стек технологий

- Python 3.10, Django 4.2, Django REST Framework 3.14
- Аутентификация: JWT (Simple JWT + Djoser)
- Документация: drf-spectacular (Swagger / Redoc)
- Фильтрация: django-filter
- БД: SQLite (dev)

## Модели

### Kittygram (базовый проект)
- **Cat** — котик (имя, цвет, год рождения, владелец)
- **Achievement** — достижение котика
- **AchievementCat** — связь котиков и достижений (M2M)

### Wishlist (расширение)
- **Need** — нужда приюта (название, категория, приоритет, статус, количество, единица измерения, автор)
- **Contribution** — вклад в закрытие нужды (количество, комментарий, автор)

## API эндпоинты

### Кошки
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/cats/` | Список котиков |
| POST | `/api/cats/` | Создать котика (auth) |
| GET | `/api/cats/{id}/` | Детали котика |
| PUT/PATCH | `/api/cats/{id}/` | Обновить котика (owner) |
| DELETE | `/api/cats/{id}/` | Удалить котика (owner) |
| GET | `/api/achievements/` | Список достижений |

### Wishlist
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/needs/` | Список нужд (фильтрация, поиск, пагинация) |
| POST | `/api/needs/` | Создать нужду (auth) |
| GET | `/api/needs/{id}/` | Детали нужды с вкладами |
| PUT/PATCH | `/api/needs/{id}/` | Обновить нужду (автор) |
| DELETE | `/api/needs/{id}/` | Удалить нужду (автор) |
| **POST** | **`/api/needs/{id}/contribute/`** | **Внести вклад (кастомное действие)** |
| GET | `/api/needs/{id}/history/` | История вкладов |
| GET | `/api/needs/urgent/` | Срочные открытые нужды |
| GET | `/api/contributions/` | Все вклады (только чтение) |

### Аутентификация
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/auth/users/` | Регистрация |
| POST | `/api/auth/jwt/create/` | Получить JWT-токен |
| POST | `/api/auth/jwt/refresh/` | Обновить токен |

### Документация
- Swagger UI: `/api/docs/`
- Redoc: `/api/redoc/`

## Примеры запросов

### Регистрация и получение токена
```bash
# Регистрация
curl -X POST http://127.0.0.1:8000/api/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "volonteer", "password": "mypass123!"}'

# Получение токена
curl -X POST http://127.0.0.1:8000/api/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"username": "volonteer", "password": "mypass123!"}'
```
Ответ:
```json
{
    "refresh": "eyJ0eXAiOiJKV1Qi...",
    "access": "eyJ0eXAiOiJKV1Qi..."
}
```

### Создание нужды
```bash
curl -X POST http://127.0.0.1:8000/api/needs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "title": "Сухой корм Royal Canin",
    "description": "Для котят до 1 года",
    "category": "food",
    "priority": "urgent",
    "quantity_required": 20,
    "unit": "kg"
  }'
```
Ответ (201 Created):
```json
{
    "id": 1,
    "title": "Сухой корм Royal Canin",
    "description": "Для котят до 1 года",
    "category": "food",
    "priority": "urgent",
    "status": "open",
    "quantity_required": 20,
    "unit": "kg",
    "quantity_fulfilled": 0,
    "quantity_remaining": 20,
    "progress": 0.0,
    "created_by": "volonteer",
    "contributions": []
}
```

### Внести вклад (кастомное действие)
```bash
curl -X POST http://127.0.0.1:8000/api/needs/1/contribute/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"quantity": 5, "comment": "От души!"}'
```
Ответ (201 Created):
```json
{
    "id": 1,
    "contributor": "volonteer",
    "quantity": 5,
    "comment": "От души!",
    "created_at": "2026-03-14T17:50:52Z"
}
```

### Фильтрация нужд
```bash
# По категории
curl http://127.0.0.1:8000/api/needs/?category=food

# По приоритету
curl http://127.0.0.1:8000/api/needs/?priority=urgent

# По статусу
curl http://127.0.0.1:8000/api/needs/?status=open

# Поиск по тексту
curl http://127.0.0.1:8000/api/needs/?search=корм
```

## Права доступа

| Роль | Котики | Нужды | Вклады |
|------|--------|-------|--------|
| Аноним | чтение | чтение | чтение |
| Пользователь | создание | создание, contribute | создание (через contribute) |
| Автор/Владелец | редактирование, удаление | редактирование, удаление | — |

## Валидации

1. **Год рождения котика** — не в будущем и не старше 40 лет
2. **Уникальность котика** — один владелец не может иметь двух котиков с одинаковым именем
3. **Количество вклада** — больше нуля и не превышает остаток нужды
4. **Уникальность нужды** — один пользователь не может создать две нужды с одинаковым названием
5. **Закрытая нужда** — нельзя вносить вклад в уже закрытую нужду

## Как запустить проект

```bash
# Клонировать репозиторий
git clone <url>
cd kittygram

# Виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Зависимости
pip install -r requirements.txt

# Настройка окружения
cp .env.example .env
# Отредактировать .env при необходимости

# Миграции и суперпользователь
python manage.py migrate
python manage.py createsuperuser

# Запуск
python manage.py runserver
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| SECRET_KEY | Секретный ключ Django | insecure-key |
| DEBUG | Режим отладки | True |
| ALLOWED_HOSTS | Разрешённые хосты | * |

Пример в файле `.env.example`.
