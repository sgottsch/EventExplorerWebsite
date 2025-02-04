"""
WSGI config for event_explorer project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# sys.path.append() # add if needed


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_explorer.settings')

application = get_wsgi_application()
