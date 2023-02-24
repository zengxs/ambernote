from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers

from ambernote.authx.models import User
from .base import BaseViewSet, NoteSpaceParameter, NoteSpaceRelatedModelViewSetMixin
from ..models import NoteSpace, NoteSpaceMember


class MemberRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteSpaceMember
        fields = ('id', 'notespace', 'user', 'role', 'created_at', 'updated_at')
        read_only_fields = fields

    notespace = serializers.SlugRelatedField(slug_field='uuid', read_only=True)
    user = serializers.SlugRelatedField(slug_field='uuid', read_only=True)


class MemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteSpaceMember
        fields = ('user', 'role', 'notespace')
        write_only_fields = fields

    notespace = serializers.SlugRelatedField(slug_field='uuid', queryset=NoteSpace.objects.all())
    user = serializers.SlugRelatedField(slug_field='uuid', queryset=User.objects.all())


class MemberUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteSpaceMember
        fields = ('role',)
        write_only_fields = fields


class MemberViewSet(NoteSpaceRelatedModelViewSetMixin, BaseViewSet):
    lookup_field = 'id'
    queryset = NoteSpaceMember.objects.order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['create']:
            return MemberCreateSerializer
        if self.action in ['update', 'partial_update']:
            return MemberUpdateSerializer
        # otherwise
        return MemberRetrieveSerializer

    @swagger_auto_schema(
        operation_description=_(
            'List all members of the notespace (Role 1 is owner, 2 is member, 3 is guest).'
        ),
        manual_parameters=[NoteSpaceParameter])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
