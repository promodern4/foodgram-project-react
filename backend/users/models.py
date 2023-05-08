from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Администратор'
    USER = 'user', 'Пользователь'


class User(AbstractUser):

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта'
    )
    role = models.CharField(
        max_length=50,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Роль'
    )

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',
                       'password',
                       'first_name',
                       'last_name',
                       ]

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_is_not_me'
            ),
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_user'
            )
        ]
