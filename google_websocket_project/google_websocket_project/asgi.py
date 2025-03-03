"""
ASGI config for google_websocket_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'google_websocket_project.settings')
django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.middleware import JWTAuthMiddlewareStack
from chat.routing import websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddlewareStack(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
