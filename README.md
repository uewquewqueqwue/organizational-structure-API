# Organizational Structure API

REST API для управления организационной структурой компании (подразделения и сотрудники).

## Возможности

- Управление подразделениями (CRUD, дерево с глубиной вложенности)
- Управление сотрудниками
- Перемещение подразделений
- Каскадное удаление и перенос сотрудников
- Документированное API (OpenAPI)

## Стек

- Python 3.13
- Django 6.0.2
- Django REST Framework
- PostgreSQL 17
- Docker + docker-compose

## Установка и запуск

### Склонируйте репозиторий
```bash
git clone <https://github.com/uewquewqueqwue/organizational-structure-API>
cd organizational-structure-API
```

### Настройка окружения
```bash
cp .env.example .env
# И заменить шаблон
```

### Запуск через Docker
```bash
docker-compose up -d

# Логи API
docker-compose logs -f web
```

## Эндпоинты API

### Документация и схема
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/schema/` | Скачать .yaml схему |
| GET | `/api/docs/` | Документация сгенирированнная `drf-spectacular`, по мимо базовой от REST API |

### Подразделения
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/departments/` | Список подразделений |
| POST | `/api/departments/` | Создать подразделение |
| GET | `/api/departments/{id}/` | Детали подразделения (с depth и include_employees) |
| PATCH | `/api/departments/{id}/` | Обновить подразделение |
| DELETE | `/api/departments/{id}/?mode=cascade/reassign` | Удалить подразделение |

### Параметры GET /departments/{id}/
- `depth` (int, default=1) — глубина вложенных подразделений (max 5)
- `include_employees` (bool, default=true) — включать сотрудников

### Удаление подразделения
- `mode=cascade` — каскадное удаление (сотрудники + дочерние подразделения)
- `mode=reassign&reassign_to_department_id={id}` — перенос сотрудников в другой отдел

### Сотрудники
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/departments/{id}/employees/` | Создать сотрудника в подразделении |

## Тестирование

```bash
# Все тесты
docker-compose exec web python manage.py test api.tests -v 2

# Точечный тест
docker-compose exec web python manage.py test api.tests.test_departments.DepartmentTest.test_create_department
```