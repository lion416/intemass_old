import os,sys
PROJECTPATH = os.path.dirname(__file__)

# Note: DEBUG now determined by absence of python -O switch
## OLD: DEBUG = False
DEBUG = __debug__

ADMINS = (
    ('Vaim', 'dev@v-aim.com'),
    #('Swagat', 'swagat@egrovesystems.com'),
    # ('sengottuvel', 'sengottuvel@egrovesystems.com'),
)

if 'test' in sys.argv:
    DATABASES = {
         'default':{
             'ENGINE': 'django.db.backends.sqlite3'
         }
    }
else:
    DATABASES = {
        'default': {
            'STORAGE_ENGINE': 'MyISAM', # used for south InnoDB would recommended
            'ENGINE': 'django.db.backends.mysql',     # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            # 'NAME': 'intemass_live',               # Or path to database file if using sqlite3.
            'NAME': 'intemass_live_merge',               # Or path to database file if using sqlite3.
            'USER': 'intemass_dbuser',               # Not used with sqlite3.
            'PASSWORD': 'Intemass@234',                # Not used with sqlite3.
            'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                               # Set to empty string for default. Not used with sqlite3
        }
    }


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    #'intemass.common.middlewares.swfupload.SWFUploadMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_nose',
    'intemass.common',
    'intemass.portal',
    'intemass.teacher',
    'intemass.student',
    'intemass.classroom',
    'intemass.itempool',
    'intemass.question',
    'intemass.paper',
    'intemass.assignment',
    'intemass.algo',
    'intemass.report',
    'intemass.mcq',
    'intemass.cpm',
    #'debug_toolbar',
    'intemass.entity',
    'intemass.canvas',

    # at the end
    'south'
)

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECTPATH, "images"),
    #os.path.join(PROJECTPATH, "static"),
    # os.path.join(PROJECTPATH, "static/images"),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s][%(name)s#%(funcName)s (%(lineno)d)] - %(levelname)s : %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level': 'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'intemass': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'intemass': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
   }
}

# Note: by default intepython is run with -O switch (see ~/public_html/intepython.fcgi).
# The console not used to avoid overwhelming bluehost apache logs.
# Based on http://stackoverflow.com/questions/5739830/simple-log-to-file-example-for-django-1-3
if DEBUG:
    LOGGING['handlers']['logfile'] = {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': PROJECTPATH + "/django.log",
            'maxBytes': 10485760,
            'backupCount': 2,
            'formatter': 'verbose',
        };
    LOGGING['loggers']['intemass'] = {
        'handlers': ['logfile'],
        'level': 'DEBUG',
        'handlers': ['logfile'],
        'level': 'DEBUG',
        };
        
