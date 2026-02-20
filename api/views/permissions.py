from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly
from typing import Any, Literal


class ReadOnlyOrAuth(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, *args) -> Any | Literal[True]:
        if request.method in SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated
