from django.urls import path 
from . import views
from .views import LakesViews, LakeMeasurementsViews, LakeDetailView, LakeMeasurementExport

# define the urls
urlpatterns = [
    path('lakes/', LakesViews.as_view()),
    path('lakes/<int:pk>/', LakeDetailView.as_view()),
    path('lakemeasurements/', LakeMeasurementsViews.as_view()),
    path('lakemeasurements/<int:pk>/<str:interval>/', LakeMeasurementsViews.as_view()),
    path('lakemeasurements/<int:pk>/<str:interval>/export/', LakeMeasurementExport.as_view(), name="lake-measurement-export"),
]