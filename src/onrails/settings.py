import os
import environ
import datetime
import threading

from decouple import config
from cloudant.client import CouchDB
from .impartial import LOGGER, PARTITION_KEY_DICT

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.system("py3clean " + str(BASE_DIR))
print("[SETTINGS] Cleared previous cache")
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(env('DEBUG')))

# ALLOWED_HOSTS = [
#     '127.0.0.1'
# ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'trains.apps.TrainsConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'onrails.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'templates') ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'onrails.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.sqlite3",
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
    }
}
COUCHDB = {
    'HOST' : "http://localhost",
    'PORT': "5984",
    'DEFAULT_CLIENT': CouchDB(env('DB_USER'), env('DB_PASSWORD'), url = env('DB_URL'), connect = True)
}
COUCHDB['USER_INFO'] = COUCHDB['DEFAULT_CLIENT']['user_info']
COUCHDB['TRAIN_DATA'] = COUCHDB['DEFAULT_CLIENT']['train_data']
COUCHDB['USER_ACTIVITY'] = COUCHDB['DEFAULT_CLIENT']['user_activity']
COUCHDB['OVERALL_SPOTTING'] = COUCHDB['DEFAULT_CLIENT']['overall_spotting']

COUCH_HOST = "http://localhost"
COUCH_PORT = "5984"
# COUCH_HOST = env('DB_HOST')
# COUCH_PORT = env('DB_PORT')

ONRAILS_CLIENT = CouchDB(env('DB_USER'), env('DB_PASSWORD'), url = env('DB_URL'), connect = True)
COUCH_USER_INFO = ONRAILS_CLIENT['user_info']
COUCH_TRAIN_DATA = ONRAILS_CLIENT['train_data']
COUCH_USER_ACTIVITY = ONRAILS_CLIENT['user_activity']
COUCH_OVERALL_SPOTTING = ONRAILS_CLIENT['overall_spotting']

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [ os.path.join(BASE_DIR, 'static/') ]

# Global Constants
ENCRYPT_KEY = env('ENCRYPT_KEY')