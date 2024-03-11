from django.urls import path
from api import views

urlpatterns = [
    path('reviews/', views.ReviewList.as_view()),
    path('reviews/<int:pk>/', views.ReviewDetail.as_view()),
    path('qrgenerator/', views.QRGenerator.as_view())
]
