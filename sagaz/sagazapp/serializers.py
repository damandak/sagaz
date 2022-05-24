from rest_framework import routers,serializers,viewsets
from rest_framework.serializers import SerializerMethodField

from .models import Lake,LakeMeasurement


class LakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lake
        fields = '__all__'

class LakeMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LakeMeasurement
        fields = ('lake', 'date', 'water_level', 'water_temperature', 'atmospheric_pressure', 'atmospheric_temperature', 'precipitation', 'alert_status')

    def create(self, validated_data):
        old_lake_m = LakeMeasurement.objects.filter(lake=validated_data['lake'], date=validated_data['date']).first()
        if old_lake_m is None:
            return LakeMeasurement.objects.create(**validated_data)
        else:
            if 'water_level' in validated_data:
                old_lake_m.water_level = validated_data['water_level']
            if 'water_temperature' in validated_data:
                old_lake_m.water_temperature = validated_data['water_temperature']
            if 'atmospheric_pressure' in validated_data:
                old_lake_m.atmospheric_pressure = validated_data['atmospheric_pressure']
            if 'atmospheric_temperature' in validated_data:
                old_lake_m.atmospheric_temperature = validated_data['atmospheric_temperature']
            if 'precipitation' in validated_data:
                old_lake_m.precipitation = validated_data['precipitation']
            if 'alert_status' in validated_data:
                old_lake_m.alert_status = validated_data['alert_status']
            old_lake_m.save()
            return old_lake_m