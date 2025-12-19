from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
# Create your views here.

# Créer un user de test au démarrage (une seule fois)
try:
    User.objects.get(username='test') #pseudo
except User.DoesNotExist:
    User.objects.create_user(username='test', password='test') #Mot de passe

def login_page(request):
    return render(request, 'login.html')

def main_page(request):
    return render(request, 'main.html')

def login_page(request):
    error = None
    print(f"Méthode: {request.method}")
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"Username reçu: {username}")
        print(f"Password reçu: {password}")
        
        user = authenticate(
            username=username,
            password=password
        )
        
        print(f"User authentifié: {user}")
        
        if user is not None:
            login(request, user)
            return redirect('/main/')
        else:
            return render(request, "login.html", {"error": "Login incorrect"})

    return render(request, "login.html")

@login_required(login_url='/login/')
def main_page(request):
    # Exemple de données ESP - à remplacer par tes vraies données de BDD
    esp_devices = [
        {'id': 1, 'name': 'ESP32 Salon', 'status': 'online', 'ip': '192.168.1.10'},
        {'id': 2, 'name': 'ESP32 Cuisine', 'status': 'offline', 'ip': '192.168.1.11'},
        {'id': 3, 'name': 'ESP8266 Chambre', 'status': 'online', 'ip': '192.168.1.12'},
    ]
    
    # Filtrer selon les permissions de l'user (à adapter selon ton modèle)
    # Pour l'instant on affiche tout
    user_devices = esp_devices
    
    return render(request, 'main.html', {'devices': user_devices, 'username': request.user.username})

def add_device(request):
    # Vue pour ajouter un appareil
    return render(request, 'add_device.html')

@login_required(login_url='/login/')
def main_page(request):
    # Données d'exemple - remplace par tes vraies données
    esp_devices = [
        {'id': 1, 'name': 'ESP32 Salon', 'status': 'online', 'ip': '192.168.1.10'},
        {'id': 2, 'name': 'ESP32 Cuisine', 'status': 'offline', 'ip': '192.168.1.11'},
    ]
    
    return render(request, 'main.html', {
        'devices': esp_devices, 
        'username': request.user.username
    })

def mqtt_page(request):
    return HttpResponse("Page MQTT")