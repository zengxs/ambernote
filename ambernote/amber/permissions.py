from typing import Optional

from rest_framework.permissions import IsAuthenticated

from .models import NoteSpace, NoteSpaceMember


class NoteSpaceMemberPermissionMixin:
    def get_member(self, user, obj) -> Optional[NoteSpaceMember]:
        """
        Get note space member object for request.user and obj related note space.
        """
        if isinstance(obj, NoteSpace):
            space = obj
        elif hasattr(obj, 'notespace'):
            if not isinstance(obj.notespace, NoteSpace):
                return None
            space = obj.notespace
        else:
            return None

        member = NoteSpaceMember.objects.filter(notespace=space, user=user).first()
        return member


class IsNoteSpaceOwner(NoteSpaceMemberPermissionMixin, IsAuthenticated):
    """ Allows access only to note space owners. """

    def has_object_permission(self, request, view, obj):
        member = self.get_member(request.user, obj)
        if member is None:
            return False
        return member.role == NoteSpaceMember.Role.OWNER


class IsNoteSpaceMember(NoteSpaceMemberPermissionMixin, IsAuthenticated):
    """ Allows access only to note space members. """

    def has_object_permission(self, request, view, obj):
        member = self.get_member(request.user, obj)
        if member is None:
            return False
        return member.role in (NoteSpaceMember.Role.OWNER, NoteSpaceMember.Role.MEMBER)


class IsNoteSpaceGuest(NoteSpaceMemberPermissionMixin, IsAuthenticated):
    """ Allows access only to note space guests. """

    def has_object_permission(self, request, view, obj):
        member = self.get_member(request.user, obj)
        if member is None:
            return False
        return member.role in (NoteSpaceMember.Role.OWNER, NoteSpaceMember.Role.MEMBER, NoteSpaceMember.Role.GUEST)


class IsAdminUserOrSelf(IsAuthenticated):
    """ Allows access only to admin users or self. """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return request.user == obj
