import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = 'Hasker'

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'drf_yasg',
    'rest_framework',
    'rest_framework.authtoken',


    'questions.apps.QuestionsConfig',
    'users.apps.UsersConfig',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'questions.middleware.Error404Exception',
    'questions.middleware.TrendingQuestions',
]

ROOT_URLCONF = 'hasker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, 'questions/templates/questions'),
                 os.path.join(BASE_DIR, 'users/templates/users'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'hasker.wsgi.application'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# REST Framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}

# JWT
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1)
}

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

AUTH_USER_MODEL = 'users.UserWithAvatar'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_URL = '/static/'

MEDIA_ROOT = 'media'
MEDIA_URL = '/media/'

BASE_USER_PHOTO = '/static/img/logo_white.png'
LOGIN_URL = '/users/login'

# EMAIL
EMAIL_HOST = ''
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_TEMPLATE = "<p>Hey, we get new answer on your question:</p> " \
                 "<p><b>{question_text}</p></b><br>" \
                 "<p>You can go by this link and read an answer:<p>" \
                 "<p><a href='{link}'>read answer</a></p><br>" \
                 "<p>---</p><br>" \
                 "<p>This is automatic message, please do ot answer</p>"

# NEW VARS
QUESTION_BATCH = 20
SEARCH_BATCH = 20
ANSWERS_BATCH = 30
TRENDING_BATCH = 20

# number of pages where too much results
# example, current page = 4 and number of pages 3 - and we can see pages 2, 3, 4
NUMBER_PAGES = 5

# import local settings fot server
try:
    from .local_settings import *
except ImportError:
    pass
