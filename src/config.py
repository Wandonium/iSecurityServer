import os

class Development(object):
  """
  Development environment configuration
  """
  DEBUG = True
  TESTING = False
  JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
  UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')

class Production(object):
  """
  Production environment configurations
  """
  DEBUG = False
  TESTING = False
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
  SQLALCHEMY_TRACK_MODIFICATIONS=False
  JWT_SECRECT_KEY = os.getenv('JWT_SECRET_KEY')
  UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')

class Testing(object):
  """
  Testing environment configuration
  """
  TESTING = True
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_TEST_URL')
  SQLALCHEMY_TRACK_MODIFICATIONS=False
  JWT_SECRECT_KEY = os.getenv('JWT_SECRET_KEY')
  UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')


app_config = {
  'development':Development,
  'production': Production,
  'testing': Testing
}