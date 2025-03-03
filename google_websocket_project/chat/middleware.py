from django.contrib.auth.models import AnonymousUser, User
from channels.db import database_sync_to_async
from channels.auth import AuthMiddlewareStack
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs

class JWTAuthMiddleware:
    """Custom middleware to authenticate WebSocket users via JWT token."""

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]

        scope["user"] = await self.get_user(token)
        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_user(self, token):
        """Extract user from JWT token."""
        if not token:
            return AnonymousUser()

        try:
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token["user_id"])
            return user
        except Exception:
            return AnonymousUser()

# Apply the JWT Middleware
def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
