# views.py
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User,MessageUser
def show_last_message(request):
    messages = MessageUser.objects.all().order_by('created_at')  # Hammasini olish
    message_data = []

    for msg in messages:
        message_data.append({
            'id': msg.id,
            'text': msg.text,
            'taken_by': msg.taken_by.username if msg.taken_by else None
        })

    return render(request, 'list.html', {'messages': message_data})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username, password=password)
            request.session['user_id'] = user.id  # foydalanuvchini sessionda saqlaymiz
            return redirect('show_last_message')
        except User.DoesNotExist:
            messages.error(request, "Foydalanuvchi yoki parol noto'g'ri!")

    return render(request, 'login.html')
def logout_view(request):
    logout(request)
    return redirect("login")