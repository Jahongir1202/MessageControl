# views.py
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User,MessageUser
def show_last_message(request):
    last_message = MessageUser.objects.last()  # Get the last message from DB
    if last_message:
        taken_by = last_message.taken_by.username if last_message.taken_by else None
        message = {'text': last_message.text, 'taken_by': taken_by}
    else:
        message = 'Hech qanday xabar mavjud emas.'

    return render(request, 'list.html', {'message': message})


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