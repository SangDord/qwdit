import os

_dbdir = os.path.abspath(os.path.dirname('.'))

SECRET_KEY = 'your_secret_key'
DATABASE_URI = 'sqlite:///' + os.path.join(_dbdir, 'qwdit.db')
DATABASE_CONNECT_OPTIONS = {'echo': False}

del os