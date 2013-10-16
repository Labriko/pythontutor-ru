#
import os
import sys

path = '/var/www'
if path not in sys.path:
    sys.path.append(path)

path = '/usr/local/python2.7-web/web/lib/python2.7/site-packages/Django-1.3.1-py2.7.egg/django'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'pylernu.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
