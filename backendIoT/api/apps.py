from django.apps import AppConfig
import threading


def start_mqtt_subscriber():
    """Démarre le subscriber MQTT dans un thread séparé"""
    import paho.mqtt.client as mqtt
    import json
    from api.models import Device, Sensor, Measurement
    
    def on_connect(client, userdata, flags, rc, properties=None):
        print(f"✅ Connecté MQTT code {rc}")
        result, mid = client.subscribe("ynov/home/sensors")
        print(f"📡 Subscribe result: {result}, mid: {mid}")

    def on_message(client, userdata, msg):
        print(f"📨 TOPIC reçu: {msg.topic}")
        print(f"📨 PAYLOAD brut: {msg.payload.decode()}")
        try:
            payload = json.loads(msg.payload.decode())
            data_str = payload['msg']  # "21°C, 50%, Y"
            parts = [p.strip() for p in data_str.replace('°C', '').split(', ')]
            temp = float(parts[0])
            hum = float(parts[1].rstrip('%'))
            presence = 1.0 if parts[2] == 'Y' else 0.0

            print(f"📡 Reçu: T={temp}°C H={hum}% P={presence}")

            try:
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
            except Device.DoesNotExist:
                print("⚠️ Device 'Test Indoor' non trouvé. Créez-le d'abord dans l'admin Django.")
            except Sensor.DoesNotExist as e:
                print(f"⚠️ Capteur non trouvé: {e}")
            except Exception as e:
                print(f"❌ Erreur lors de l'enregistrement: {e}")
        except Exception as e:
            print(f"❌ Erreur de parsing: {e}")

    def run_mqtt_client():
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
            client.on_connect = on_connect
            client.on_message = on_message
            
            try:
                client.connect("localhost", 1883, 60)
                client.loop_start()
                print("🚀 Subscriber MQTT démarré ! En attente de messages...")
                
                # Garder le thread actif
                import time
                while True:
                    time.sleep(1)
            except ConnectionRefusedError:
                print("⚠️ Impossible de se connecter au broker MQTT (localhost:1883). Assurez-vous que le broker est démarré.")
            except Exception as e:
                print(f"❌ Erreur de connexion MQTT: {e}")
        except KeyboardInterrupt:
            print("⏹️ Arrêt du subscriber MQTT...")
            client.loop_stop()
            client.disconnect()

    # Démarrer le subscriber dans un thread séparé
    mqtt_thread = threading.Thread(target=run_mqtt_client, daemon=True)
    mqtt_thread.start()


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        """Démarre le subscriber MQTT quand l'application Django est prête"""
        # Éviter de démarrer plusieurs fois (notamment lors des migrations)
        import os
        if os.environ.get('RUN_MAIN') == 'true':
            # Ne démarrer que dans le processus principal (pas dans le reloader)
            try:
                start_mqtt_subscriber()
            except Exception as e:
                print(f"⚠️ Erreur lors du démarrage du subscriber MQTT: {e}")