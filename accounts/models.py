from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


# Кастомная промежуточная модель для groups
class CustomUserGroups(models.Model):
    """Промежуточная модель для связи CustomUser и Group"""
    customuser = models.ForeignKey('CustomUser', on_delete=models.CASCADE, db_column='user_id')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, db_column='group_id')

    class Meta:
        db_table = 'auth_user_groups'
        unique_together = [['customuser', 'group']]


# Кастомная промежуточная модель для user_permissions
class CustomUserUserPermissions(models.Model):
    """Промежуточная модель для связи CustomUser и Permission"""
    customuser = models.ForeignKey('CustomUser', on_delete=models.CASCADE, db_column='user_id')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, db_column='permission_id')

    class Meta:
        db_table = 'auth_user_user_permissions'
        unique_together = [['customuser', 'permission']]


class CustomUser(AbstractUser):
    """Кастомная модель пользователя"""
    
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='user_set',
        related_query_name='user',
        through='CustomUserGroups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='user_set',
        related_query_name='user',
        through='CustomUserUserPermissions',
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'auth_user'