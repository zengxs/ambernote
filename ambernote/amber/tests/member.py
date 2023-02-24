from django.test import TestCase
from rest_framework.test import APIClient

from ambernote.authx.models import User
from ..models import NoteSpace, NoteSpaceMember


class MemberTestCase(TestCase):
    fixtures = [
        'testdata-1.yaml',
    ]

    def setUp(self):
        self.client = APIClient()

    def test_admin(self):
        self.client.force_login(User.objects.filter(pk=1).first())  # as admin
        self._test_add_member_success()
        self._test_list_members_success()
        self._test_read_member_success()

    def test_owner(self):
        self.client.force_login(User.objects.filter(pk=2).first())  # as owner
        self._test_add_member_success()
        self._test_list_members_success()
        self._test_read_member_success()

    def test_member(self):
        self.client.force_login(User.objects.filter(pk=3).first())  # as member
        self._test_add_member_denied()
        self._test_list_members_success()
        self._test_read_member_success()

    def test_guest(self):
        self.client.force_login(User.objects.filter(pk=4).first())  # as guest
        self._test_add_member_denied()
        self._test_list_members_success()
        self._test_read_member_success()

    def test_other_user(self):
        self.client.force_login(User.objects.filter(pk=5).first())  # not belong to notespace
        self._test_add_member_denied()
        self._test_list_members_denied()
        self._test_read_member_denied()

    def _test_add_member_success(self):
        data = {
            'notespace': NoteSpace.objects.filter(pk=1).first().uuid,
            'user': User.objects.filter(pk=5).first().uuid,
            'role': NoteSpaceMember.Role.GUEST,
        }
        response = self.client.post('/api/members/', data=data)
        self.assertEqual(response.status_code, 201)  # Created

        # check saved data
        member = NoteSpaceMember.objects.filter(
            notespace__uuid=data['notespace'],
            user__uuid=data['user'],
        ).first()
        self.assertIsNotNone(member)
        self.assertEqual(member.role, data['role'])

    def _test_add_member_denied(self):
        data = {
            'notespace': NoteSpace.objects.filter(pk=1).first().uuid,
            'user': User.objects.filter(pk=5).first().uuid,
            'role': NoteSpaceMember.Role.GUEST,
        }
        response = self.client.post('/api/members/', data=data)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def _test_list_members_success(self):
        notespace = NoteSpace.objects.filter(pk=1).first()
        response = self.client.get('/api/members/', data={'notespace': notespace.uuid})
        self.assertEqual(response.status_code, 200)  # OK

    def _test_list_members_denied(self):
        notespace = NoteSpace.objects.filter(pk=1).first()
        response = self.client.get('/api/members/', data={'notespace': notespace.uuid})
        self.assertEqual(response.status_code, 403)

    def _test_read_member_success(self):
        response = self.client.get('/api/members/1/')
        self.assertEqual(response.status_code, 200)  # OK

    def _test_read_member_denied(self):
        response = self.client.get('/api/members/1/')
        self.assertEqual(response.status_code, 403)
