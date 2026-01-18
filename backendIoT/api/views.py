from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.utils import timezone
from datetime import timedelta
from .models import Measurement

def register_page(request):
    """Page d'inscription pour créer un nouveau compte"""
    if request.user.is_authenticated:
        return redirect('/main/')
    
    error = None
    success = None
    
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        # Validation
        if not username:
            error = "Le nom d'utilisateur est requis"
        elif len(username) < 3:
            error = "Le nom d'utilisateur doit contenir au moins 3 caractères"
        elif User.objects.filter(username=username).exists():
            error = "Ce nom d'utilisateur est déjà utilisé"
        elif not email:
            error = "L'email est requis"
        elif User.objects.filter(email=email).exists():
            error = "Cet email est déjà utilisé"
        elif not password:
            error = "Le mot de passe est requis"
        elif len(password) < 6:
            error = "Le mot de passe doit contenir au moins 6 caractères"
        elif password != password_confirm:
            error = "Les mots de passe ne correspondent pas"
        else:
            # Vérifier le format de l'email
            try:
                validate_email(email)
            except ValidationError:
                error = "Format d'email invalide"
        
        if not error:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                messages.success(request, "Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
                return redirect('/login/')
            except Exception as e:
                error = f"Erreur lors de la création du compte : {str(e)}"
    
    return render(request, "register.html", {"error": error, "success": success})

def login_page(request):
    """Page de connexion"""
    if request.user.is_authenticated:
        return redirect('/main/')
    
    error = None
    
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            error = "Veuillez remplir tous les champs"
        else:
            user = authenticate(
                username=username,
                password=password
            )
            
            if user is not None:
                login(request, user)
                return redirect('/main/')
            else:
                error = "Nom d'utilisateur ou mot de passe incorrect"
    
    return render(request, "login.html", {"error": error})

def logout_page(request):
    """Déconnexion de l'utilisateur"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès")
    return redirect('/login/')

@login_required(login_url='/login/')
def main_page(request):
    # Récupérer les dernières données MQTT pour les cartes
    recent = timezone.now() - timedelta(minutes=15)
    data = Measurement.objects.filter(
        timestamp__gte=recent
    ).select_related('sensor').order_by('-timestamp')
    
    sensors = {}
    for m in data:
        st = m.sensor.sensor_type
        if st not in sensors:
            sensors[st] = {'latest': float(m.value), 'time': m.timestamp.isoformat()}
    
    # Récupérer l'historique des mesures pour le tableau
    # Par défaut : dernières 100 mesures
    filter_sensor = request.GET.get('sensor', '')
    filter_period = request.GET.get('period', '')
    
    history_query = Measurement.objects.all().select_related('sensor').order_by('-timestamp')
    
    # Filtrer par capteur
    if filter_sensor:
        history_query = history_query.filter(sensor__sensor_type=filter_sensor)
    
    # Filtrer par période
    if filter_period == '24h':
        history_query = history_query.filter(timestamp__gte=timezone.now() - timedelta(hours=24))
    elif filter_period == '7j':
        history_query = history_query.filter(timestamp__gte=timezone.now() - timedelta(days=7))
    elif filter_period == '30j':
        history_query = history_query.filter(timestamp__gte=timezone.now() - timedelta(days=30))
    
    # Limiter à 100 dernières mesures pour les performances
    history_measurements = history_query[:100]
    
    # Préparer les données pour le template
    history_data = []
    for m in history_measurements:
        sensor_type_display = {
            'temperature': 'Température',
            'humidity': 'Humidité',
            'presence': 'Présence',
            'light': 'Luminosité',
            'sound': 'Niveau sonore'
        }.get(m.sensor.sensor_type, m.sensor.sensor_type.capitalize())
        
        # Formater la valeur selon le type
        if m.sensor.sensor_type == 'temperature':
            value_display = f"{m.value:.1f} °C"
        elif m.sensor.sensor_type == 'humidity':
            value_display = f"{m.value:.1f} %"
        elif m.sensor.sensor_type == 'presence':
            value_display = "Oui" if m.value >= 1 else "Non"
        else:
            value_display = f"{m.value:.2f}"
        
        history_data.append({
            'timestamp': m.timestamp,
            'timestamp_iso': m.timestamp.isoformat(),
            'sensor_type': sensor_type_display,
            'sensor_type_raw': m.sensor.sensor_type,
            'value': value_display,
            'value_raw': m.value
        })
    
    return render(request, 'main.html', {
        'username': request.user.username,
        'sensor_data': sensors,
        'history_data': history_data,
        'current_filter_sensor': filter_sensor,
        'current_filter_period': filter_period
    })

def add_device(request):
    # Vue pour ajouter un appareil
    return render(request, 'add_device.html')


def mqtt_page(request):
    return HttpResponse("Page MQTT")