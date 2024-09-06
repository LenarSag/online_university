
# Проект Онлайн Университет позволяет пользователю приобретать курсы и получать доступ к онлайн урокам

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)  ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)

### Описание проекта
Проект представляет собой площадку для размещения онлайн-курсов с набором уроков. Доступ к урокам предоставляется после покупки курса (подписки). Внутри курса студенты автоматически распределяются по группам.

### Возможности проекта: 

Можно зарегистрироваться и авторизоваться, приобрести понравившийся курс и начать изучать по онлайн урокам. Админ может создавать/менять/удалять курсы, уроки и группы к ним.

API для Онлайн Университет написан с использованием библиотеки **FastAPI**, используется **JWTAuthentication** для аутентификации.

### Технологии

- Python 3.9
- FastAPI
- SqlAlchemy


### __OpenAPI документация__
* Swagger: http://127.0.0.1:8000/docs/
* ReDoc: http://127.0.0.1:8000/redoc/


### Запуск проекта в dev-режиме

Клонировать репозиторий и перейти в него в командной строке: 
```
git clone git@github.com:LenarSag/foodgram_fastapi.git
```
Cоздать и активировать виртуальное окружение: 
```
python3.9 -m venv venv 
```
* Если у вас Linux/macOS 

    ```
    source venv/bin/activate
    ```
* Если у вас windows 
 
    ```
    source venv/scripts/activate
    ```
```
python3.9 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```

Запуск проекта:


```
python main.py
```
