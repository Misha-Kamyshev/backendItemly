"""
Модуль для загрузки и хранения конфигурационных параметров приложения.

Загружает переменные окружения из файла .env и предоставляет доступ
к критически важным конфигурационным данным для работы приложения.

Импорты:
    - os: Для работы с переменными окружения и системными функциями
    - dotenv.load_dotenv: Для загрузки переменных окружения из файла .env

Переменные:
    - DATA_SOURCE: DSN строка для подключения к базе данных

Функции:
    - load_dotenv: Загружает переменные окружения из указанного файла
"""

import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi_jwt import JwtAccessBearerCookie, JwtRefreshBearerCookie

load_dotenv('.env')

SQLALCHEMY_DSN=os.getenv('SQLALCHEMY_DSN')
ASYNC_PG_DSN=os.getenv('ASYNC_PG_DSN')

SECRET_KEY_ACCESS = os.getenv('SECRET_KEY_ACCESS')
SECRET_KEY_REFRESH = os.getenv('SECRET_KEY_REFRESH')

access_security = JwtAccessBearerCookie(
    secret_key=SECRET_KEY_ACCESS,
    algorithm='HS256',
    access_expires_delta=timedelta(minutes=15)
)

refresh_security = JwtRefreshBearerCookie(
    secret_key=SECRET_KEY_REFRESH,
    algorithm='HS256',
    access_expires_delta=timedelta(days=15)
)
