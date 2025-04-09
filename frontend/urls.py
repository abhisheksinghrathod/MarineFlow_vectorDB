from django.urls import path
from .views import index

urlpatterns = [
    path("chatbot/", index, name="chatbot_ui"),
]
