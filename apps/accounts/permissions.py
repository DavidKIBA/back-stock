from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Réservé aux administrateurs uniquement"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
 
 
class IsManagerOrAbove(BasePermission):
    """Manager et Admin"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_manager
 
 
class IsAuthenticated(BasePermission):
    """Tout utilisateur connecté (tous les profils)"""
    def has_permission(self, request, view):
        return request.user.is_authenticated
 
 
class ReadOnlyOrManager(BasePermission):
    """
    GET → tout le monde connecté
    POST/PUT/DELETE → Manager et Admin seulement
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.is_manager
