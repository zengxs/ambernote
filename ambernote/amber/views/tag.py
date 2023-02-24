from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, serializers
from rest_framework.permissions import IsAdminUser

from .base import BaseViewSet, NoteSpaceParameter, NoteSpaceRelatedModelViewSetMixin
from ..models import NoteSpace, Tag
from ..permissions import IsNoteSpaceMember


class TagCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'notespace')
        write_only_fields = fields

    notespace = serializers.SlugRelatedField(slug_field='uuid', queryset=NoteSpace.objects.all())


class TagRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('uuid', 'name', 'notespace', 'created_at', 'updated_at')
        read_only_fields = fields

    notespace = serializers.SlugRelatedField(slug_field='uuid', read_only=True)


class TagViewSet(NoteSpaceRelatedModelViewSetMixin, BaseViewSet):
    lookup_field = 'uuid'
    queryset = Tag.objects.order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['create']:
            return TagCreateSerializer
        # otherwise
        return TagRetrieveSerializer

    def get_write_permissions(self):
        """
        Tag can be created by any member of the notespace.
        """
        return [permissions.OR(IsAdminUser(), IsNoteSpaceMember())]

    @swagger_auto_schema(
        operation_description=_('List all tags of the notespace.'),
        manual_parameters=[NoteSpaceParameter])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
