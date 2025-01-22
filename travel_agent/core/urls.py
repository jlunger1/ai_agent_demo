from django.urls import path
from .views import ask, start_session

urlpatterns = [
    path('ask/', ask, name='ask'),
    path('start_session/', start_session, name='start_session')
]
