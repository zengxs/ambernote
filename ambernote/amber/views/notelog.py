from django.http import Http404
from rest_framework import permissions, serializers
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from .base import BaseViewSet, NoteSpaceRelatedModelViewSetMixin
from ..models import Note, NoteLog


class NoteLogRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteLog
        fields = ('uuid', 'note', 'user', 'action', 'extras', 'created_at', 'updated_at')
        read_only_fields = fields

    note = serializers.SlugRelatedField(slug_field='uuid', read_only=True)
    user = serializers.SlugRelatedField(slug_field='uuid', read_only=True)


class NoteLogViewSet(NoteSpaceRelatedModelViewSetMixin, BaseViewSet):
    lookup_field = 'uuid'
    queryset = NoteLog.objects.order_by('-created_at')

    def get_serializer_class(self):
        return NoteLogRetrieveSerializer

    def get_write_permissions(self):
        """
        NoteLog should not be written by API.
        """
        return [permissions.NOT(AllowAny())]

    def list(self, request, *args, **kwargs):
        """
        List all note logs.
        """
        if 'note' not in request.query_params:
            raise serializers.ValidationError('`note` query parameter is required.')
        try:
            note = Note.objects.get(uuid=request.query_params['note'])
        except Note.DoesNotExist:
            raise Http404
        # check if the user has permission to access the note
        self.check_notespace_perms(note.notespace)
        # only list logs of the note
        self.queryset = self.queryset.filter(note=note)

        return ModelViewSet.list(self, request, *args, **kwargs)
