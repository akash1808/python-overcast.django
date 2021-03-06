from django.contrib.auth.models import User, Group
from rest_framework import serializers, fields
from rest_framework_nested import relations

from . import models

class SimpleListField(serializers.ListField):
    child = serializers.CharField()

    def to_internal_value(self, data):
        return  ' '.join(data)

    def to_representation(self, data):
        if isinstance(data, list):
            return data
        return data.split(' ')


class MirrorSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.URLField(required=True)
    series = SimpleListField(required=True)
    components = SimpleListField(required=True)
    public = serializers.BooleanField(default=False)
    refresh_in_progress = serializers.BooleanField(read_only=True)

    class Meta:
        model = models.Mirror
        fields = ('self', 'url', 'series', 'components', 'public', 'refresh_in_progress')

class MirrorField(serializers.HyperlinkedRelatedField):
    def get_queryset(self):
        if hasattr(self, 'context') and 'request' in self.context:
            return models.Mirror.objects.filter(owner=self.context['request'].user)

        return super(MirrorField, self).get_queryset()


class MirrorSetSerializer(serializers.HyperlinkedModelSerializer):
    mirrors = MirrorField(many=True, view_name='mirror-detail', queryset=models.Mirror.objects.all())

    class Meta:
        model = models.MirrorSet
        fields = ('self', 'mirrors')


class SnapshotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Snapshot
        fields = ('self', 'timestamp', 'mirrorset')
