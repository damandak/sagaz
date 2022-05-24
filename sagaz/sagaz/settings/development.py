from .base_settings import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-r$8agt-+!l(lzt843(j_@w%m-n&t1o6w_hc(@x&9_m_u_e!k)8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mysqldb',
        'USER': 'root',
        'PASSWORD': 'adminroot',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}