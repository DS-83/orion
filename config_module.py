import os

class Config(object):
    """Base config"""

    CELERY_BROKER_URL='redis://localhost:6379'
    CELERY_RESULT_BACKEND='redis://localhost:6379'
    LANGUAGES = {
                'ru': 'Russian',
                'en': 'English'
                }
    DEBUG = False
    TESTING = False
    KEY_P=b'cXhd_G3PU4U-6QWPHfgNz8BcHOAZV1I0zN0o6u5CC3c='

class DevelopmentConfig(Config):
    """Development config"""
    ENV = 'development'
    DEBUG = True
    DATABASE=os.path.join('./instance', 'app.sqlite')



class ProductionConfig(Config):
    """Production config"""
    DATABASE=os.path.join('./instance', 'app.sqlite_prod')
