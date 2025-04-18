from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import login_view, logout_view

urlpatterns = [
    path('messages/', views.show_last_message, name='show_last_message'),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('my-messages/', views.my_messages_view, name='my_messages'),
    path('edit-message/<int:msg_id>/', views.edit_message, name='edit_message'),
    path('delete-message/<int:msg_id>/', views.delete_message, name='delete_message'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)