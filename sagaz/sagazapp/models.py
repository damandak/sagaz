from django.db import DJANGO_VERSION_PICKLE_KEY, models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
import pytz

# from django.core.mail import send_mail
# from background_task import background
# from asgiref.sync import sync_to_async
# from twilio.rest import Client


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
    image = models.ImageField(upload_to='lake_images', blank=True, null=True)
    sagaz_id = models.CharField(max_length=255, blank=True, null=True, unique=True) # id that comes from the API
    country = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True) # political region in country
    # Location data
    lat = models.FloatField(blank=True, null=True, verbose_name="Latitude (decimal degrees)")
    lon = models.FloatField(blank=True, null=True, verbose_name="Longitude (decimal degrees)")
    altitude = models.FloatField(blank=True, null=True, verbose_name="Altitude (meters)") # in meters
    # Dynamic fields
    area = models.FloatField(blank=True, null=True, verbose_name="Area (square kilometers)") # km2 - NO HISTÓRICO
    volume = models.FloatField(blank=True, null=True, verbose_name="Water Volume (millions of cubic meters)") # water volume in millions of cubic meters - NO HISTÓRICO
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    station_status = models.CharField(max_length=255, default="Instalación Programada", blank=True, null=True, verbose_name="Station status (Ej: Operativa, Instalación Programada, Operativa sin Pluviómetro, etc)")
    current_alert_status = models.CharField(max_length=255, default="Verde", blank=True, null=True, verbose_name="Current alert status (Debe empezar con 'Verde', 'Amarillo' o 'Rojo'. Otros quedarán en gris)")

    def __str__(self):
        return self.name
    def get_last_alert_status(self):
        last_valid_measurement = LakeMeasurement.objects.filter(lake=self).exclude(alert_status=None).order_by('-date').first()
        return last_valid_measurement.alert_status
    def get_health_status(self):
        return self.HEALTH_CHOICES[self.health_status][1]

    # When saving, send alert by sms depending on current alert status
    def save(self, *args, **kwargs):
        super(Lake, self).save(*args, **kwargs)
        # if it starts with Rojo
        # if self.current_alert_status.startswith("Rojo"):
        #     self.send_alert_by_sms()
        #     self.send_alert_by_email()

    # async def send_alert_by_sms(self):
    #     # Function to send an SMS message
    #     # client = Client(account_sid, auth_token)
    #     # message = await client.messages.create(to=to, from_=from_number, body=body)
    #     # return message
    #     return True

    # @background(schedule=60)
    # def send_alert_by_email(self):
    #     subject = 'SAGAZ - Alerta en ' + self.name
    #     message = ('Alerta de GLOF en ' + self.name + ' en ' + self.region + ', ' + self.country + '.'
    #         + 'La alerta es de nivel ' + self.current_alert_status + '.'
    #         + 'Para más información, visite https://www.sagaz.org/lake/' + str(self.id))
    #     from_email = 'damirmandakovic@gmail.com'
    #     recipient_list = ['receiver@example.com']
    #     send_mail(subject, message, from_email, recipient_list)
    #     print("Email sent")

class LakeMeasurement(BaseModel):
    lake = models.ForeignKey(Lake, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=False, null=False)

    water_level = models.FloatField(blank=True, null=True, verbose_name="Water Level (meters)") # in meters
    water_temperature = models.FloatField(blank=True, null=True, verbose_name="Water Temperature (Celsius") # in Celsius
    atmospheric_pressure = models.FloatField(blank=True, null=True, verbose_name="Atmospheric Pressure (hPa)") # in hPa
    atmospheric_temperature = models.FloatField(blank=True, null=True, verbose_name="Atmospheric Temperature (Celsius)") # in Celsius
    precipitation = models.FloatField(blank=True, null=True, verbose_name="Precipitation (milimeters)") # in mm

    alert_status = models.CharField(max_length=255, blank=True, null=True, default="Verde (inicial)", verbose_name="Alert Status (Debe empezar con 'Verde', 'Amarillo' o 'Rojo'. Otros quedarán en gris)")

    class Meta:
        ordering = ['-date']
        
    def __str__(self) -> str:
        tz = pytz.timezone('America/Santiago')
        return f"{self.date.astimezone(tz).strftime('%Y-%m-%d %H:%M')} - {self.lake.name}"

    # update lake current_alert_status when changing alert_status
    def save(self, *args, **kwargs):
        super(LakeMeasurement, self).save(*args, **kwargs)
        self.lake.current_alert_status = self.lake.get_last_alert_status()
        self.lake.save()
