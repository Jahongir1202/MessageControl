from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import User, MessageUser

def show_last_message(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    all_messages = MessageUser.objects.all().order_by('-created_at')
    visible_messages = [
        msg for msg in all_messages
        if msg.taken_by is None or msg.taken_by.id == user_id
    ]

    return render(request, 'list.html', {
        'messages': visible_messages,
        'user_id': user_id
    })

def my_messages_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    my_messages = MessageUser.objects.filter(taken_by_id=user_id).order_by('-created_at')
    return render(request, 'my_messages.html', {'messages': my_messages})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            return redirect('show_last_message')
        except User.DoesNotExist:
            messages.error(request, "Foydalanuvchi yoki parol noto'g'ri!")
    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()
    return redirect("login")

def edit_message(request, msg_id):
    user_id = request.session.get('user_id')
    message = get_object_or_404(MessageUser, id=msg_id, taken_by_id=user_id)

    if request.method == 'POST':
        new_text = request.POST.get('text')
        if new_text:
            message.text = new_text
            message.save()
            return redirect('my_messages')

    return render(request, 'edit.html', {'message': message})

def delete_message(request, msg_id):
    user_id = request.session.get('user_id')
    message = get_object_or_404(MessageUser, id=msg_id, taken_by_id=user_id)
    message.delete()
    return redirect('my_messages')
