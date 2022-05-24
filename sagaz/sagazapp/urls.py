from django.urls import path 
from . import views
from .views import LakeMeasurementsViews

# define the urls
urlpatterns = [
    path('lakes/', views.lakes),
    path('lakes/<int:pk>/', views.lake_detail),
    path('lakemeasurements/', LakeMeasurementsViews.as_view())
]