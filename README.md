
# Yatube 
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)

## Описание:
Учебный проект, созданный в рамках учебы в Яндекс.Практикуме.
Yatube - социальная сеть, где пользователи могут оставлять посты, комментарии к ним и подписываться на интересных авторов. У каждого пользователя есть персональная страничка.

## Зависимости:
Django 2.2<br>
Pytest 6.2

## Стэк технологий:
**Frontend:** HTML, CSS
**Backend:** Python, Django, Pytest

## Скриншоты:
Главная страница
![Main page screenshot](https://i120.fastpic.org/big/2022/0707/4b/d6ac81f786b9ae700eebfae6049ac94b.jpg)

Страница регистрации
![Registration screenshot](https://i120.fastpic.org/big/2022/0707/a4/8593213ae16222727c35700f5b94e0a4.jpg)

Страница поста
![Post detail screenshot](https://i120.fastpic.org/big/2022/0707/c8/3bedf7b2d483b2bd4252cdf20466bbc8.jpg)

## Автор: Серова Екатерина

## Обратная связь:
Если у вас есть предложения или замечания, пожалуйста, свяжитесь со мной - katyaserova@yandex.ru

## Запуск проекта в dev-режиме

Клонировать репозиторий

```bash
  git clone https://github.com/EISerova/hw05_final
```

Перейти в папку проекта

```bash
  cd hw05_final
```

Создать и активировать виртуальное окружение

```bash
  python3 -m venv env
  source env/bin/activate
```

Установить зависимости

```bash
  python -m pip install --upgrade pip
  pip install -r requirements.txt
```

Выполнить миграции

```bash
  cd yatube
  python manage.py migrate
```

Запустить сервер

```bash
  python manage.py runserver
```

## Лицензия:
[MIT](https://choosealicense.com/licenses/mit/)
