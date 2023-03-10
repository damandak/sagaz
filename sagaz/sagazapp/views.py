from distutils.log import error
from django.shortcuts import render
# parsing data from the client
from rest_framework.parsers import JSONParser
# To bypass having a CSRF token
from django.views.decorators.csrf import csrf_exempt
# for sending response to the client
from django.http import HttpResponse
# API definition for the lake model
from .serializers import LakeSerializer, LakeMeasurementSerializer
# Lake model
from .models import Lake, LakeMeasurement

# Import datetime
from datetime import datetime, timedelta

from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.response import Response
from rest_framework import status


@csrf_exempt
def lake_detail(request, pk):
  try:
    # obtain the lake with the passed id.
    lake = Lake.objects.get(pk=pk)
  except:
    # respond with a 404 error message
    return HttpResponse(status=404)  

class LakeDetailView(APIView):
  permission_classes = [HasAPIKey]

  def get(self, request, pk):
    try:
      # obtain the lake with the passed id.
      lake = Lake.objects.get(pk=pk)
    except:
      # respond with a 404 error message
      return HttpResponse(status=404)  
    # serialize the lake
    serializer = LakeSerializer(lake, context={'request': request})
    # return the serialized lake
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)


############################################################################################
#                               API MEDICIONES - > SAGAZAPP                                #                                        
############################################################################################

class LakesViews(APIView):
  permission_classes = [HasAPIKey]

  def get(self, request, format=None):
    lakes = Lake.objects.all()
    serializer = LakeSerializer(lakes, many=True)
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

  def post(self, request, format=None):
    sagaz_id = request.data['sagaz_id']
    new_data = request.data
    if Lake.objects.filter(sagaz_id=sagaz_id).exists():
      serializer = LakeSerializer(data=new_data)
      if serializer.is_valid():
        serializer.save()
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
      else:
        return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    else:
      error_data_msg = "Lake with sagaz id '" + sagaz_id + "' does not exist"
      return Response({"status": "error", "data": error_data_msg}, status=status.HTTP_400_BAD_REQUEST)

class LakeMeasurementsViews(APIView):
  permission_classes = [HasAPIKey]

  def post(self, request, format=None):
    sagaz_id = request.data['sagaz_id']
    new_data = request.data.copy()
    if Lake.objects.filter(sagaz_id=sagaz_id).exists():
      lake = Lake.objects.get(sagaz_id=sagaz_id)
      new_data['lake'] = lake.id
      serializer = LakeMeasurementSerializer(data=new_data)
      if serializer.is_valid():
        serializer.save()
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
      else:
        return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    else:
      error_data_msg = "Lake with sagaz id '" + sagaz_id + "' does not exist"
      return Response({"status": "error", "data": error_data_msg}, status=status.HTTP_400_BAD_REQUEST)
    
  def get(self, request, pk, interval):
    try:
      # obtain the lake with the passed id.
      lake = Lake.objects.get(pk=pk)
      if interval == 'daily':
        measurements = LakeMeasurement.objects.filter(lake=lake).filter(date__gte=datetime.now() - timedelta(days=1)).order_by('date')
      elif interval == 'weekly':
        measurements = LakeMeasurement.objects.filter(lake=lake).filter(date__gte=datetime.now() - timedelta(days=7)).order_by('date')
      elif interval == 'biweekly':
        measurements = LakeMeasurement.objects.filter(lake=lake).filter(date__gte=datetime.now() - timedelta(days=14)).order_by('date')
      elif interval == 'monthly':
        measurements = LakeMeasurement.objects.filter(lake=lake).filter(date__gte=datetime.now() - timedelta(days=30)).order_by('date')
      elif interval == 'yearly':
        measurements = LakeMeasurement.objects.filter(lake=lake).filter(date__gte=datetime.now() - timedelta(days=365)).order_by('date')
      elif interval == 'all':
        measurements = LakeMeasurement.objects.filter(lake=lake).order_by('date')
    except:
      # respond with a 404 error message
      return HttpResponse(status=404)  
    # serialize the lake
    serializer = LakeMeasurementSerializer(measurements, many=True)
    # return the serialized lake measurements
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
  
  def delete(self, request):
    try:
      # obtain the lake with the passed id.
      lake = Lake.objects.get(sagaz_id=request.data['sagaz_id'])
      lakemeasurement = LakeMeasurement.objects.filter(lake=lake, date=request.data['date']).first()
      if lakemeasurement is not None:
        lakemeasurement.delete()
        return Response({"status": "success", "data": "Measurement " + str(request.data['sagaz_id']) + " " + str(request.data['date']) + " deleted"}, status=status.HTTP_200_OK)
      else:
        return Response({"status": "error", "data": "Measurement " + str(request.data['sagaz_id']) + " " + str(request.data['date']) + " not found"}, status=status.HTTP_404_NOT_FOUND)
    except:
      # respond with a 404 error message
      return Response({"status": "error", "data": "Problem with request, probably measurement not found"}, status=status.HTTP_404_NOT_FOUND)

  def patch(self, request):
    try:
      # obtain the lake with the passed id.
      sagaz_id = request.data['sagaz_id']
      new_data = request.data.copy()
      if Lake.objects.filter(sagaz_id=sagaz_id).exists():
        lake = Lake.objects.get(sagaz_id=sagaz_id)
        prev_measurement = LakeMeasurement.objects.get(lake=lake, date=request.data['date'])
        new_data['lake'] = lake.id
        serializer = LakeMeasurementSerializer(instance=prev_measurement, data=new_data)
        if serializer.is_valid():
          serializer.save()
          return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
          return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
      else:
        error_data_msg = "Lake with sagaz id '" + sagaz_id + "' does not exist"
        return Response({"status": "error", "data": error_data_msg}, status=status.HTTP_400_BAD_REQUEST)
    except:
      # respond with a 404 error message
      return Response({"status": "error", "data": "Problem with request, probably measurement not found"}, status=status.HTTP_404_NOT_FOUND)
