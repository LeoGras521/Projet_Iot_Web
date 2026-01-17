import os
import sys

# 1. AJUSTE PATH si besoin (ajoute dossier projet)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 2. Settings AVANT TOUT import Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backendIoT.settings')

import django
django.setup()

# 3. MAINTENANT imports models OK
import paho.mqtt.client as mqtt
import json
from datetime import datetime
from api.models import Sensor, Measurement

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"✅ Connecté MQTT code {rc}")
    result, mid = client.subscribe("ynov/home/sensors")
    print(f"📡 Subscribe result: {result}, mid: {mid}")


def on_message(client, userdata, msg):
    print(f"📨 TOPIC reçu: {msg.topic}")
    print(f"📨 PAYLOAD brut: {msg.payload.decode()}")
    print(f"🔥 MESSAGE REÇU SUR '{msg.topic}' : {msg.payload.decode()}")
    try:
        payload = json.loads(msg.payload.decode())
        data_str = payload['msg']  # "21°C, 50%, Y"
        parts = [p.strip() for p in data_str.replace('°C', '').split(', ')]
        temp = float(parts[0])
        hum = float(parts[1].rstrip('%'))
        presence = 1.0 if parts[2] == 'Y' else 0.0

        print(f"📡 Reçu: T={temp}°C H={hum}% P={presence}")

        device = Device.objects.get(name="Test Indoor") 
        sensors = {
            'temperature': Sensor.objects.get(device=device, sensor_type='temperature'),
            'humidity': Sensor.objects.get(device=device, sensor_type='humidity'),
            'presence': Sensor.objects.get(device=device, sensor_type='presence')
        }

        Measurement.objects.create(sensor=sensors['temperature'], value=temp)
        Measurement.objects.create(sensor=sensors['humidity'], value=hum)
        Measurement.objects.create(sensor=sensors['presence'], value=presence)
        
        print("💾 3 mesures stockées!")
    except Exception as e:
        print(f"❌ Erreur: {e}")

# Device import après setup
from api.models import Device

import paho.mqtt.client as mqtt
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start()

import time
try:
    print("🚀 Subscriber prêt ! Publie MQTTX...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("⏹️ Arrêt...")
    client.loop_stop()
    client.disconnect()