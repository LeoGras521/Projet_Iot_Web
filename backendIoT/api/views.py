from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Create your views here.

# Créer un user de test au démarrage (une seule fois)
try:
    User.objects.get(username='test')
except User.DoesNotExist:
    User.objects.create_user(username='test', password='test')

def login_page(request):
    return render(request, 'login.html')

def main_page(request):
    return render(request, 'main.html')

def login_page(request):
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