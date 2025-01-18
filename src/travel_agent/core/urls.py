from django.urls import path
from .views import process_query

urlpatterns = [
    path("process-query/", process_query, name="process_query"),
]
