![Foodgram workflow](https://github.com/xeniakutsevol/yamdb_final/actions/workflows/foodgram_workflow.yml/badge.svg)

# Запуск docker-compose для Foodgram

### Описание проекта

Проект **Foodgram** (Продуктовый помощник) - это онлайн-сервис для неравнодушных к домашней кухне и кулинарии. Пользователи публикуют, просматривают, добавляют в избранное понравившиеся рецепты, формируют удобный для скачивания список покупок, подписываются на публикации понравившихся авторов. Приятного аппетита!

Проект помещен в контейнеры docker-compose для упрощения развертывания.

### Используемые технологии
- Django
- Django Rest Framework
- Djoser
- Docker
- React

### Как запустить проект:

Клонировать репозиторий:

```
git clone https://github.com/xeniakutsevol/foodgram-project-react
```

Создать файл .env в каталогe infra и добавить в него переменную SECRET_KEY=<random_string>:

```
cd infra
```

```
touch .env
```

```
nano .env
```

Дефолтное значение SECRET_KEY герерируется автоматически с помощью get_random_secret_key() из django.core.management.utils, если не задать свое.


Перейти в репозиторий с Dockerfile и собрать образ:

```
cd backend/foodgram/
```

```
docker build -t foodgram .
```

Запустить контейнеры docker-compose:

```
cd ../../infra/
```

```
docker-compose up -d --build
```

Cоздать суперпользователя:

```
docker-compose exec web python manage.py createsuperuser
```

Залить данные из БД (на этапе сборки контейнера фикстуры ингредиентов уже предзагружены):

```
docker-compose exec web python manage.py loaddata fixtures.json
```

Проверить работоспособность проекта:

```
http://localhost/
```

```
http://localhost/admin/
```

Образы проекта также доступен в DockerHub:

```
xeniakutsevol/foodgram_backend:v1.00.0000
```

```
xeniakutsevol/foodgram_frontend:v1.00.0000
```

### Как пользоваться проектом

Документация к Foodgram:

```
http://localhost/api/docs
```