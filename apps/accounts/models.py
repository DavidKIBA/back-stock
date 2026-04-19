from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    ROLE_ADMIN        = 'ADMIN'
    ROLE_MANAGER      = 'MANAGER'
    ROLE_GESTIONNAIRE = 'GESTIONNAIRE'
 
    ROLES = [
        (ROLE_ADMIN,        'Administrateur'),
        (ROLE_MANAGER,      'Manager'),
        (ROLE_GESTIONNAIRE, 'Gestionnaire Stock'),
    ]

    role = models.CharField(max_length=20, choices=ROLES, default=ROLE_GESTIONNAIRE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN
    
    @property
    def is_manager(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_MANAGER]
    
    @property
    def is_gestionnaire(self):
        return True  # Tous les utilisateurs ont accès aux fonctionnalités de gestionnaire
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
