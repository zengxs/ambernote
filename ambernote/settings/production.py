import logging

from django.core.management.utils import get_random_secret_key

from .common import *  # noqa

logger = logging.getLogger(__name__)

# Colors for terminal output
# https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal

RED_COLOR = '\33[91m'
FRED_COLOR = '\033[101m'
YELLOW_COLOR = '\033[93m'
RESET_COLOR = '\033[0m'

WARNING_HEADER = (f'{RED_COLOR}==================== {RESET_COLOR}{FRED_COLOR}'
                  f'WARNING{RESET_COLOR}{RED_COLOR} ====================\n')
WARNING_FOOTER = f'{RED_COLOR}================================================={RESET_COLOR}\n'

# Debug setting
# https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/#debug
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allowed hosts
# https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/#allowed-hosts
os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

logger.info(f'ALLOWED_HOSTS: {ALLOWED_HOSTS}')

# Secret key
# https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/#secret-key

if 'SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ['SECRET_KEY']
    logger.info('SECRET_KEY found in environment')
else:
    SECRET_KEY = get_random_secret_key()
    logger.warning(
        f'{WARNING_HEADER}'
        'SECRET_KEY not found in environment\n'
        'We generated a random SECRET_KEY for you:\n'
        f'  {YELLOW_COLOR}{SECRET_KEY}{RED_COLOR}\n'
        'Generated SECRET_KEY should be used for testing only\n'
        'Don\'t use generated SECRET_KEY in real production\n'
        f'{WARNING_FOOTER}'
    )

# Caches
# https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/#caches
# https://docs.djangoproject.com/en/4.1/topics/cache/#setting-up-the-cache
# https://docs.djangoproject.com/en/4.1/ref/settings/#caches
#
# CACHES has been configured in common.py for various environments
# We only need to override it by CACHE_URL environment variable

if 'CACHE_URL' not in os.environ:
    # print red warning message
    logger.warning(
        f'{WARNING_HEADER}'
        'CACHE_URL should be explicitly set in production environment\n'
        'Currently we use default cache configuration in common.py (local memory)\n'
        'All cache in local memory will be lost when server restarts\n'
        'DO NOT use it in production\n'
        f'{WARNING_FOOTER}'
    )

# Databases
# https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/#databases
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
#
# DATABASES has been configured in common.py for various environments
# We only need to override it by DATABASE_URL environment variable

if 'DATABASE_URL' not in os.environ:
    # print red warning message
    logger.warning(
        f'{WARNING_HEADER}'
        'DATABASE_URL should be explicitly set in production environment\n'
        'Currently we use default database configuration in common.py (SQLite)\n'
        'DO NOT use it in production\n'
        f'{WARNING_FOOTER}'
    )
