from django.db import transaction
from rest_framework import serializers
from rest_framework.permissions import IsAdminUser

from .base import BaseViewSet
from ..models import NoteSpace, NoteSpaceMember


class EmbeddedMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteSpaceMember
        fields = ('id', 'user', 'role')
        read_only_fields = fields

    user = serializers.SlugRelatedField(slug_field='uuid', queryset=NoteSpaceMember.objects.all())
    role = serializers.ChoiceField(choices=NoteSpaceMember.Role.choices)


class NoteSpaceRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteSpace
        fields = ('uuid', 'type', 'name', 'created_at', 'updated_at', 'members')
        read_only_fields = fields

    members = EmbeddedMemberSerializer(many=True, read_only=True)


class NoteSpaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteSpace
        fields = ('type', 'name')
        write_only_fields = fields


class NoteSpaceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteSpace
        fields = ('name',)
        write_only_fields = fields


class NoteSpaceViewSet(BaseViewSet):
    lookup_field = 'uuid'
    queryset = NoteSpace.objects.order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['create']:
            return NoteSpaceCreateSerializer
        if self.action in ['update', 'partial_update']:
            return NoteSpaceUpdateSerializer
        # otherwise
        return NoteSpaceRetrieveSerializer

    def get_list_permissions(self):
        """
        Only admin user can list all note spaces.
        """
        return [IsAdminUser()]

    def get_create_permissions(self):
        """
        Only admin user can create a note space.
        """
        return [IsAdminUser()]

    def perform_create(self, serializer):
        """
        Create a note space and add the creator as a owner of the note space.
        """
        with transaction.atomic():
            # Create the note space
            space = NoteSpace(**serializer.validated_data)
            space.save()
            # Add the creator as a owner of the note space
            member = NoteSpaceMember(notespace=space, user=self.request.user, role=NoteSpaceMember.Role.OWNER)
            member.save()
