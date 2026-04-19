from .base import *  # noqa

DEBUG = True

CORS_ALLOW_ALL_ORIGINS = True  # allow any origin in dev

# Faster password hasher in tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Optional: log SQL queries in dev
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',  # set to DEBUG to see SQL
        },
    },
}
