from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# DEVICE(id, name, ip_address, ..., owner_id)
# SENSOR(id, name, sensor_type, device_id)
# MEASUREMENT(id, value, timestamp, sensor_id)
# THRESHOLD(id, min_value, max_value, sensor_id)
# ALERT(id, message, severity, device_id, sensor_id)
# COMFORT_INDEX(id, index_value, device_id)
# DEVICE_PAIRING(id, pairing_code, device_id)
# USER(id, username, ...)



class Device(models.Model):
    name = models.CharField(max_length=100)          # Nom de l’ESP (ex: "ESP Salon")
    ip_address = models.GenericIPAddressField()      # IP locale
    mac_address = models.CharField(max_length=50, blank=True)
    mqtt_client_id = models.CharField(max_length=100, blank=True)
    wifi_ssid = models.CharField(max_length=100, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('online', 'Online'), ('offline', 'Offline')],
        default='offline'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Sensor(models.Model):
    SENSOR_TYPES = [
        ('temperature', 'Température'),
        ('humidity', 'Humidité'),
        ('light', 'Luminosité'),
        ('sound', 'Niveau sonore'),
        ('presence', 'Présence'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sensors')
    name = models.CharField(max_length=100)                  # ex: "DHT22 salon"
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPES)
    unit = models.CharField(max_length=20, blank=True)       # °C, %, dB, lux, etc.
    mqtt_topic = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.device.name} - {self.name}"

class Measurement(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='measurements')
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()                 # Pour présence, tu peux mettre 0/1

    def __str__(self):
        return f"{self.sensor} @ {self.timestamp} = {self.value}"


class ComfortIndex(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='comfort_indexes')
    timestamp = models.DateTimeField(auto_now_add=True)
    index_value = models.FloatField()          # ex: 0–100
    comment = models.CharField(max_length=200, blank=True)  # "Confortable", "Trop chaud", etc.

    def __str__(self):
        return f"{self.device.name} - {self.index_value} @ {self.timestamp}"


class Threshold(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='thresholds')
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    level = models.CharField(
        max_length=20,
        choices=[('green', 'Vert'), ('orange', 'Orange'), ('red', 'Rouge')],
        default='green'
    )
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Seuil {self.sensor} ({self.level})"


class Alert(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alerts')
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=255)
    severity = models.CharField(
        max_length=20,
        choices=[('info', 'Info'), ('warning', 'Warning'), ('critical', 'Critical')],
        default='warning'
    )
    acknowledged = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert {self.device.name} - {self.message}"


class DevicePairing(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='pairing')
    pairing_code = models.CharField(max_length=50, blank=True)     # code ou QR
    wifi_ssid = models.CharField(max_length=100)
    wifi_password = models.CharField(max_length=100)
    mqtt_broker = models.CharField(max_length=200)
    mqtt_port = models.IntegerField(default=1883)
    mqtt_username = models.CharField(max_length=100, blank=True)
    mqtt_password = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Appairage {self.device.name}"

