from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone number must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser):
    first_name = models.CharField(
        max_length=30,
        verbose_name="First Name"
    )
    last_name = models.CharField(
        max_length=30,
        verbose_name="Last Name"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email Address"
    )
    phone = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Phone Number"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active"
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Is Staff"
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name="Is Superuser"
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Created"
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Date Updated"
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser or self.is_staff

    def has_module_perms(self, app_label):
        return self.is_superuser or self.is_staff
