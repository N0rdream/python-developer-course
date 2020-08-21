# Hasker

Пример .env файла
----------
```
SECRET_KEY=secret

HASKER_DATABASE_NAME=hasker
HASKER_DATABASE_USER=hasker
HASKER_DATABASE_PASSWORD=password
HASKER_DATABASE_HOST=db
HASKER_DATABASE_PORT=5432

STATIC_ROOT=/static
MEDIA_ROOT=/media

DJANGO_SETTINGS_MODULE=config.settings.staging
```

Как запустить
----------
```
$ docker-compose up --build -d
```






