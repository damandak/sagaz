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
from .models import Lake

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
            print(serializer)
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
        new_data = request.data
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


    