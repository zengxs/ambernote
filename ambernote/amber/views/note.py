from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .base import BaseViewSet, NoteSpaceParameter, NoteSpaceRelatedModelViewSetMixin
from ..models import Note, NoteLog, NoteSpace, Tag
from ..permissions import IsNoteSpaceMember


class EmbeddedTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('uuid', 'name')
        read_only_fields = fields


class NoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('title', 'content', 'notespace')
        write_only_fields = fields

    notespace = serializers.SlugRelatedField(slug_field='uuid', queryset=NoteSpace.objects.all())


class NoteRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('uuid', 'title', 'content', 'revision', 'notespace',
                  'is_archived', 'is_pinned', 'is_deleted', 'tags',
                  'created_at', 'updated_at')
        read_only_fields = fields

    notespace = serializers.SlugRelatedField(slug_field='uuid', read_only=True)
    tags = EmbeddedTagSerializer(many=True, read_only=True)


class NoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('title', 'content')
        write_only_fields = fields

    def update(self, instance, validated_data):
        with transaction.atomic():
            # check if really updated
            if any([
                instance.title != validated_data.get('title', instance.title),
                instance.content != validated_data.get('content', instance.content),
            ]):
                instance.revision += 1  # increase revision
                NoteLog.objects.create(
                    note=instance,
                    user=self.context['request'].user,
                    action=NoteLog.Action.UPDATED,
                    extras={
                        'old': {
                            'title': instance.title,
                            'content': instance.content,
                        },
                        'new': {
                            'title': validated_data.get('title', instance.title),
                            'content': validated_data.get('content', instance.content),
                        },
                    },
                )
            return super().update(instance, validated_data)


class NoteViewSet(NoteSpaceRelatedModelViewSetMixin, BaseViewSet):
    lookup_field = 'uuid'
    queryset = Note.objects.order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['create']:
            return NoteCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NoteUpdateSerializer
        # otherwise
        return NoteRetrieveSerializer

    def get_create_permissions(self):
        """
        Note can be created by any member of the notespace.
        """
        return [permissions.OR(IsAdminUser(), IsNoteSpaceMember())]

    def get_update_permissions(self):
        """
        Note can be updated by any member of the notespace.
        """
        return [permissions.OR(IsAdminUser(), IsNoteSpaceMember())]

    def get_destroy_permissions(self):
        """
        Note can be destroyed by any member of the notespace.
        User should set is_deleted to True instead of destroying the note.
        And system will destroy the note after a period of time.
        Only admin can destroy the note immediately.
        """
        return [IsAdminUser()]

    def perform_create(self, serializer):
        # Action create only perform permission check on global level.
        # So we need to check permission on object level here.
        notespace = serializer.validated_data['notespace']
        self.check_notespace_perms(notespace)

        # add note and log
        with transaction.atomic():
            note = serializer.save()
            # add log
            NoteLog.objects.create(
                note=note,
                user=self.request.user,
                action=NoteLog.Action.CREATED,
                extras={
                    'title': note.title,
                    'content': note.content,
                },
            )

    @swagger_auto_schema(
        operation_description=_(
            'List all notes in the notespace. '
            'Permission required notespace guest or above.'),
        manual_parameters=[NoteSpaceParameter])
    def list(self, request, *args, **kwargs):
        super().list(request, *args, **kwargs)

    @action(methods=['post'], detail=True, url_path='archive',
            permission_classes=[IsAdminUser | IsNoteSpaceMember])
    def archive(self, request, *args, **kwargs):
        """
        Make note as archived. Permission required notespace member or above.
        """
        return self._update_note_flag(request, 'is_archived', True, NoteLog.Action.ARCHIVED)

    @action(methods=['post'], detail=True, url_path='unarchive',
            permission_classes=[IsAdminUser | IsNoteSpaceMember])
    def unarchive(self, request, *args, **kwargs):
        """
        Make note as unarchived. Permission required notespace member or above.
        """
        return self._update_note_flag(request, 'is_archived', False, NoteLog.Action.UNARCHIVED)

    @action(methods=['post'], detail=True, url_path='pin',
            permission_classes=[IsAdminUser | IsNoteSpaceMember])
    def pin(self, request, *args, **kwargs):
        """
        Make note as pinned. Permission required notespace member or above.
        """
        return self._update_note_flag(request, 'is_pinned', True, NoteLog.Action.PINNED)

    @action(methods=['post'], detail=True, url_path='unpin',
            permission_classes=[IsAdminUser | IsNoteSpaceMember])
    def unpin(self, request, *args, **kwargs):
        """
        Make note as unpinned. Permission required notespace member or above.
        """
        return self._update_note_flag(request, 'is_pinned', False, NoteLog.Action.UNPINNED)

    @action(methods=['post'], detail=True, url_path='delete',
            permission_classes=[IsAdminUser | IsNoteSpaceMember])
    def move_to_trash(self, request, *args, **kwargs):
        """
        Move note to trash. Permission required notespace member or above.
        """
        return self._update_note_flag(request, 'is_deleted', True, NoteLog.Action.DELETED)

    @action(methods=['post'], detail=True, url_path='restore',
            permission_classes=[IsAdminUser | IsNoteSpaceMember])
    def restore(self, request, *args, **kwargs):
        """
        Restore note from trash. Permission required notespace member or above.
        """
        return self._update_note_flag(request, 'is_deleted', False, NoteLog.Action.RESTORED)

    def _update_note_flag(self, request, flag_name: str, flag_value: bool, log_action: NoteLog.Action):
        note = self.get_object()
        old_value = getattr(note, flag_name)
        if old_value != flag_value:  # only update when value changed
            with transaction.atomic():
                setattr(note, flag_name, flag_value)
                note.save()
                # add log
                NoteLog.objects.create(
                    note=note,
                    user=self.request.user,
                    action=log_action,
                )
            return Response({'ok': True, 'message': 'Success'})
        else:
            return Response({'ok': False, 'message': (
                f'The value of {flag_name} is already {flag_value}.\n'
                'That not means the operation failed, but it is not necessary to do it.'
            )}, status=status.HTTP_202_ACCEPTED)
