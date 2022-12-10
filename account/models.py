from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    """
    Usermanager to manage users
    """
    use_in_migrations = True

    def create_user(self, email, password=None):
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password
        )
        user.staff = True
        user.is_superuser=True
        user.admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """
    User Model
    """
    fullname = models.CharField(
        null=True,
        blank=True,
        max_length=512,
        help_text='Your fullname like first and last name, 512 characters.'
    )
    email = models.EmailField(max_length=254, unique=True)
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    is_active = models.BooleanField(
        default=True,
        help_text=(
            'Designates whether this user should be treated as active. '
            'Deselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['id']

    def get_fullname(self):
        return self.fullname

    def __str__(self):
        return "{} ({})".format(self.get_fullname(), self.email)
