from django.http import Http404
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from rest_framework import exceptions, permissions, viewsets
from rest_framework.permissions import IsAdminUser

from ..models import NoteSpace
from ..permissions import IsNoteSpaceGuest, IsNoteSpaceOwner

NoteSpaceParameter = openapi.Parameter(
    name='notespace',
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description=_('UUID of the notespace'),
    required=True,
)

NoteParameter = openapi.Parameter(
    name='note',
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description=_('UUID of the note'),
    required=True,
)


class BaseViewSet(viewsets.ModelViewSet):
    """Base viewset for all models"""

    ordering = ('-created_at',)

    def get_permissions(self):
        if self.action == 'list':
            return self.get_list_permissions()
        elif self.action == 'retrieve':
            return self.get_read_permissions()
        elif self.action == 'create':
            return self.get_create_permissions()
        elif self.action in ['update', 'partial_update']:
            return self.get_update_permissions()
        elif self.action == 'destroy':
            return self.get_destroy_permissions()
        else:
            # extra actions fallback to default permissions
            return super().get_permissions()

    def get_read_permissions(self):
        """
        Permissions for RETRIEVE action.
        Default permissions for LIST action.
        """
        return [permissions.OR(IsAdminUser(), IsNoteSpaceGuest())]

    def get_write_permissions(self):
        """
        Default permissions for CREATE, UPDATE, and DESTROY actions.
        """
        return [permissions.OR(IsAdminUser(), IsNoteSpaceOwner())]

    def get_list_permissions(self):
        return self.get_read_permissions()

    def get_update_permissions(self):
        return self.get_write_permissions()

    def get_destroy_permissions(self):
        return self.get_write_permissions()

    def get_create_permissions(self):
        return self.get_write_permissions()


class NoteSpaceRelatedModelViewSetMixin:
    def check_notespace_perms(self, notespace=None) -> None:
        """
        Check if the user has permission to access the notespace.
        :raises PermissionDenied: if request.user does not have required permissions
        """
        perms = self.get_permissions()
        for perm in perms:
            if callable(perm):
                perm = perm()
            if hasattr(perm, 'has_object_permission') and notespace is not None:
                if not perm.has_object_permission(self.request, self, notespace):
                    self.permission_denied(self.request, message='Permission denied')
            if hasattr(perm, 'has_permission') and not perm.has_permission(self.request, self):
                self.permission_denied(self.request, message='Permission denied')

    def list(self, request, *args, **kwargs):
        """
        Override the default list method to filter the queryset by notespace
        Action "list" only perform permission check on global level.
        So we need to check the object level permission manually here.
        """
        # check if the notespace is passed as a query parameter
        if 'notespace' not in self.request.query_params:
            raise exceptions.ParseError('Missing notespace parameter')

        try:
            notespace = NoteSpace.objects.get(uuid=self.request.query_params['notespace'])
        except NoteSpace.DoesNotExist:
            raise Http404

        # check if the user has permission to access the notespace
        self.check_notespace_perms(notespace)

        # override the queryset, so that only objects in the notespace are returned
        self.queryset = self.queryset.filter(notespace=notespace)

        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Override the default create method to add the notespace to the object
        Action "create" only perform permission check on global level.
        So we need to check the object level permission manually here.
        """
        notespace = serializer.validated_data['notespace']
        self.check_notespace_perms(notespace)
        super().perform_create(serializer)
