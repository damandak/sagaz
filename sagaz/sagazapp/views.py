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

import pandas as pd
import io

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
      lake.calculate_last_data_date()
      lake.save()
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
      lake.calculate_last_data_date()
      lake.save()
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

    last_data_date = None
    if lake.last_data_date:  # check if the date exists
        last_data_date = lake.last_data_date.strftime('%d-%m-%Y')

    # return the serialized lake measurements
    return Response({
      "status": "success",
      "data": serializer.data,
      "last_data_date": last_data_date,
    }, status=status.HTTP_200_OK)
  
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

class LakeMeasurementExport(APIView):
  def get(self, request, pk, interval):
    # Fetch the data from LakeMeasurement model
    lake_measurements = LakeMeasurement.objects.filter(lake_id=pk)
    if interval == "daily":
        start_date = datetime.now() - timedelta(days=1)
    elif interval == "weekly":
        start_date = datetime.now() - timedelta(weeks=1)
    elif interval == "biweekly":
        start_date = datetime.now() - timedelta(weeks=2)
    elif interval == "monthly":
        start_date = datetime.now() - timedelta(days=31)
    elif interval == "yearly":
        start_date = datetime.now() - timedelta(days=365)
    else:
        start_date = None
    if start_date is not None:
      lake_measurements = lake_measurements.filter(date__gte=start_date)

    def make_naive(dt):
      try:
          return dt.tz_convert(None)
      except:
          return dt
    
    # Transform the QuerySet to DataFrame
    df = pd.DataFrame(lake_measurements.values())
    df = df.applymap(make_naive)

    csv_file = io.StringIO()
    df.to_csv(csv_file, index=False)
    csv_file.seek(0)

    response = HttpResponse(csv_file.read(), content_type='text/csv')
    # include date, lake and interval in the filename
    filename = "lake_measurement_export_" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + "_" + str(pk) + "_" + str(interval) + ".csv"
    response['Content-Disposition'] = 'attachment; filename=' + filename

    return response
  