from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet)
router.register('notespaces', views.NoteSpaceViewSet)
router.register('members', views.MemberViewSet)
router.register('tags', views.TagViewSet)
router.register('notes', views.NoteViewSet)
router.register('notelogs', views.NoteLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
