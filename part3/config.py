import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-only-jwt-secret-change-me-in-production-0123456789')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@hbnb.io')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin1234')
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
}