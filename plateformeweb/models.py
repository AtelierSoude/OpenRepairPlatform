from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from address.models import AddressField
from avatar.models import AvatarField

# ------------------------------------------------------------------------------
# custom User model
# see: https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username


from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, ):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    first_name = models.CharField(_('first name'), max_length=100, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=100, blank=True, null=True)

    # https://github.com/stefanfoulis/django-phonenumber-field
    phone_number = PhoneNumberField(_("phone number"), blank=True, null=True)

    # https://github.com/furious-luke/django-address
    street_address = AddressField(_("street address"), blank=True, null=True)

    birth_date = models.DateField(_("date of birth"), blank=True, null=True)

    # http://django-avatar.readthedocs.io/en/latest/
    avatar_img = AvatarField(_("avatar"), blank=True, null=True)

    bio = models.TextField(_("bio"), blank=True, null=True)

    objects = UserManager()

# ------------------------------------------------------------------------------
