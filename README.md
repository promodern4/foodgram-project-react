# Проект Foodgram
### Описание
*Продуктовый помощник* - сайт, на котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин скачивать сводный список продуктов, необходимый для приготовления одного или нескольких выбранных блюд.
### Технологии
- Python 3.7.8
- Django 3.2
- Django Rest Framework 3.14.0
- PostgreSQL 15.2
### Локальный запуск
Клонируйте репозиторий и перейдите в него в командной строке:
```
git clone git@github.com:promodern4/foodgram-project-react.git && cd foodgram-project-react
```
Перейдите в директорию /infra_dev/:
```
cd infra_dev/
```
Для того, чтобы приложение могло работать с базой данных Postgres, оно должно знать необходимые данные для подключения к базе. Задайте необходимые настройки в файле .env.template и скопируйте его в файл .env:
```
cp .env.template .env
```
Запустите контейнеры:
```
docker compose up -d --build
```
Откройте новое окно терминала и перейдите в директорию foodgram-project-react/backend/. Установите и активируйте виртуальное окружение:
```
python -m venv venv && source venv/bin/activate
``` 
Установите зависимости:
```
pip install -r requirements.txt
````
Cоздайте суперпользователя, выполните миграции и запустите проект:
```
python manage.py createsuperuser
python manage.py migrate
python manage.py runserver
```
Протестируйте проект по адресу:
```
http://localhost/
```
### Запуск в контейнере
Клонируйте репозиторий и перейдите в него в командной строке:
```
git clone git@github.com:promodern4/foodgram-project-react.git && cd foodgram-project-react
```
Перейдите в директорию /infra/:
```
cd infra/
```
Для того, чтобы приложение могло работать с базой данных Postgres, оно должно знать необходимые данные для подключения к базе. Задайте необходимые настройки в файле .env.template и скопируйте его в файл .env:
```
cp .env.template .env
```
Запустите контейнеры:
```
docker compose up -d --build
```
Выполните миграции:
```
docker compose exec backend python manage.py migrate
```
Создайте суперпользователя:
```
docker compose exec backend python manage.py createsuperuser
```
Соберите статику:
```
docker compose exec backend python manage.py collecstatic --no-input
```
Заполните базу данных игредиентами:
```
docker compose exec backend python manage.py load_ingredients_csv
```
Создайте через окно администратора несколько тэгов.
Проверьте работу проекта по адресу:
```
http://localhost/
```
После работы с проектом создайте резервную копию базы данных:
```
docker compose exec backend python manage.py dumpdata > fixtures.json
```
Для остановки контейнеров используйте команду:
```
docker compose down -v
```
### Примеры запросов
Документация к API: [documentation](http://localhost/api/docs/)