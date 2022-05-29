from django.db import DJANGO_VERSION_PICKLE_KEY, models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class UserManager(BaseUserManager):
    def create_user(
            self, email, first_name, last_name, password=None,
            commit=True):
        """
        Creates and saves a User with the given email, first name, last name
        and password.
        """
        if not email:
            raise ValueError(_('Users must have an email address'))
        if not first_name:
            raise ValueError(_('Users must have a first name'))
        if not last_name:
            raise ValueError(_('Users must have a last name'))

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        if commit:
            user.save(using=self._db)
        return user

class Lake(BaseModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    sagaz_id = models.CharField(max_length=255, blank=True, null=True, unique=True) # id that comes from the API
    country = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True) # political region in country
    # Location data
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    altitude = models.FloatField(blank=True, null=True) # in meters
    # Dynamic fields
    area = models.FloatField(blank=True, null=True) # km2 - NO HISTÓRICO
    volume = models.FloatField(blank=True, null=True) # water volume in cubic meters - NO HISTÓRICO
    ACTIVE = 0
    INACTIVE = 1
    STATION_CHOICES = (
        # Nivel de operación
        (ACTIVE, 'Activa'),
        (INACTIVE, 'Inactiva'),
    )
    station_status = models.IntegerField(choices=STATION_CHOICES, default=ACTIVE) # NO HISTÓRICO

    def __str__(self):
        return self.name
    def get_last_alert_status(self):
        last_valid_measurement = LakeMeasurement.objects.filter(lake=self).exclude(alert_status=None).order_by('-date').first()
        return last_valid_measurement.alert_status
    def get_health_status(self):
        return self.HEALTH_CHOICES[self.health_status][1]

class LakeMeasurement(BaseModel):
    lake = models.ForeignKey(Lake, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=False, null=False)

    water_level = models.FloatField(blank=True, null=True) # in meters
    water_temperature = models.FloatField(blank=True, null=True) # in Celsius
    atmospheric_pressure = models.FloatField(blank=True, null=True) # in hPa
    atmospheric_temperature = models.FloatField(blank=True, null=True) # in Celsius
    precipitation = models.FloatField(blank=True, null=True) # in mm

    GREEN = 0
    YELLOW = 1
    RED = 2
    STATUS_CHOICES = (
        (GREEN, 'Verde'),
        (YELLOW, 'Amarilla'),
        (RED, 'Roja'),
    )
    alert_status = models.IntegerField(choices=STATUS_CHOICES, blank=True, null=True) # HISTÓRICO
