from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from ambernote.authx.models import User
from ..permissions import IsAdminUserOrSelf


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uuid', 'email', 'fullname')
        read_only_fields = ('uuid', 'email')


class UserDetailSerializer(serializers.ModelSerializer):
    """
    The serializer for the user detail view.
    It contains sensitive information, so it should only be used by the user himself.
    """

    class Meta:
        model = User
        fields = ('uuid', 'email', 'fullname', 'is_superuser', 'is_staff', 'is_active',
                  'date_joined', 'last_login', 'created_at', 'updated_at')
        read_only_fields = fields


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = User.objects.order_by('-date_joined')
    serializer_class = UserSerializer
    http_method_names = ['get', 'put', 'patch', 'head', 'options']  # no post, no delete

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return [IsAdminUserOrSelf()]
        # otherwise
        return [IsAdminUser()]

    @action(detail=False, methods=['get'], url_path='me',
            serializer_class=UserDetailSerializer,
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get the current user information.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
