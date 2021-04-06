from django.urls import path

from .views import ReportsView


urlpatterns = [
    path('reports/', ReportsView.as_view()),
]
