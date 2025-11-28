from django.shortcuts import render

# Create your views here.

def login_page(request):
    return render(request, 'login.html')

def main_page(request):
    return render(request, 'main.html')