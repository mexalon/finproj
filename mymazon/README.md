## Дипломная работа к профессии Python-разработчик «API Сервис заказа товаров для розничных сетей».

Для запуска необходимо:
1) Создать базы данных Postges и Redis (для работы Celery)
2) Прописать в настройках проекта либо задать переменные среды:
- PG_HOST = хост БД Postgres (по умолчанию '127.0.0.1')
- PG_NAME = название БД (по умолчанию 'finproj')
- PG_USER = имя пользователя БД (по умолчанию 'finproj')
- PG_PASS = пароль пользователя БД (по умолчанию 'finproj')
- PG_PORT = порт БД (по умолчанию '5432')
- REDIS_HOST = хост Redis (по умолчанию '127.0.0.1')
- REDIS_PORT = порт Redis (по умолчанию '6379')
  
  либо сразу - REDIS_URL =  вида 'redis://R_HOST:R_PORT'
- EMAIL_HOST = адрес gmail, с которого будет делаться рассылка
- EMAIL_PASSWORD = пароль от аккаунта gmail

3) Установить зависимости `pip install -r requirements.txt`
4) Создать начальние миграции `python manage.py migrate`
5) Создать себе суперпользователя `python manage.py createsuperuser`
6) Запустить рабочих Celery `celery -A mymazon  worker -l INFO`
7) Запустить сервер `python manage.py runserver`

Синтаксис запросов как в предоставленном примере.


   