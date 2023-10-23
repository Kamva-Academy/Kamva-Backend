from rest_framework import serializers


class LinkSerializer(serializers.Serializer):
    source = serializers.CharField()
    target = serializers.CharField()


class RoadmapSerializer(serializers.Serializer):
    taken_path = LinkSerializer(many=True)
