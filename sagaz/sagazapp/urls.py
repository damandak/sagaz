from django.urls import path 
from . import views
from .views import LakesViews, LakeMeasurementsViews

# define the urls
urlpatterns = [
    path('lakes/', LakesViews.as_view()),
    path('lakes/<int:pk>/', views.lake_detail),
    path('lakemeasurements/', LakeMeasurementsViews.as_view())
]