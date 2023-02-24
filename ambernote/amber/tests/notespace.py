from django.test import TestCase
from rest_framework.test import APIClient

from ambernote.amber.models import NoteSpace, NoteSpaceMember
from ambernote.authx.models import User


class NoteSpaceTestCase(TestCase):
    fixtures = (
        'testdata-1.yaml',
    )

    def setUp(self):
        self.client = APIClient()

    def test_admin(self):
        self.client.force_login(User.objects.filter(pk=1).first())  # as admin
        self._test_add_notespace_success()
        self._test_read_notespace_success()
        self._test_list_notespace_success()
        self._test_update_notespace_success()
        self._test_delete_notespace_success()

    def test_owner(self):
        self.client.force_login(User.objects.filter(pk=2).first())  # as owner
        self._test_add_notespace_denied()
        self._test_read_notespace_success()
        self._test_list_notespace_denied()
        self._test_update_notespace_success()
        self._test_delete_notespace_success()

    def test_member(self):
        self.client.force_login(User.objects.filter(pk=3).first())  # as member
        self._test_add_notespace_denied()
        self._test_read_notespace_success()
        self._test_list_notespace_denied()
        self._test_update_notespace_denied()
        self._test_delete_notespace_denied()

    def test_guest(self):
        self.client.force_login(User.objects.filter(pk=4).first())  # as guest
        self._test_add_notespace_denied()
        self._test_read_notespace_success()
        self._test_list_notespace_denied()
        self._test_update_notespace_denied()
        self._test_delete_notespace_denied()

    def test_other_user(self):
        self.client.force_login(User.objects.filter(pk=5).first())  # not belong to notespace
        self._test_add_notespace_denied()
        self._test_read_notespace_denied()
        self._test_list_notespace_denied()
        self._test_update_notespace_denied()
        self._test_delete_notespace_denied()

    def _test_add_notespace_success(self):
        data = {
            'name': 'test add notespace',
            'type': NoteSpace.Type.PERSONAL,
        }
        response = self.client.post('/api/notespaces/', data=data)
        self.assertEqual(response.status_code, 201)

        # check saved data
        notespace = NoteSpace.objects.order_by('-id').first()
        self.assertIsNotNone(notespace)
        self.assertEqual(notespace.name, data['name'])
        member = notespace.members.first()
        self.assertIsNotNone(member)
        self.assertEqual(member.role, NoteSpaceMember.Role.OWNER)

    def _test_add_notespace_denied(self):
        data = {
            'name': 'test add notespace',
            'type': NoteSpace.Type.PERSONAL,
        }
        response = self.client.post('/api/notespaces/', data=data)
        self.assertEqual(response.status_code, 403)

    def _test_read_notespace_success(self):
        notespace = NoteSpace.objects.filter(pk=1).first()
        response = self.client.get(f'/api/notespaces/{notespace.uuid}/')
        self.assertEqual(response.status_code, 200)

    def _test_read_notespace_denied(self):
        notespace = NoteSpace.objects.filter(pk=1).first()
        response = self.client.get(f'/api/notespaces/{notespace.uuid}/')
        self.assertEqual(response.status_code, 403)

    def _test_list_notespace_success(self):
        response = self.client.get('/api/notespaces/')
        self.assertEqual(response.status_code, 200)

    def _test_list_notespace_denied(self):
        response = self.client.get('/api/notespaces/')
        self.assertEqual(response.status_code, 403)

    def _test_update_notespace_success(self):
        notespace = NoteSpace.objects.filter(pk=1).first()
        data = {
            'name': 'test update notespace',
        }
        response = self.client.patch(f'/api/notespaces/{notespace.uuid}/', data=data)
        self.assertEqual(response.status_code, 200)

        # check saved data
        notespace = NoteSpace.objects.filter(pk=1).first()
        self.assertIsNotNone(notespace)
        self.assertEqual(notespace.name, data['name'])

    def _test_update_notespace_denied(self):
        notespace = NoteSpace.objects.filter(pk=1).first()
        data = {
            'name': 'test update notespace',
        }
        response = self.client.patch(f'/api/notespaces/{notespace.uuid}/', data=data)
        self.assertEqual(response.status_code, 403)

    def _test_delete_notespace_success(self):
        notespace = NoteSpace.objects.filter(pk=1).first()
        response = self.client.delete(f'/api/notespaces/{notespace.uuid}/')
        self.assertEqual(response.status_code, 204)

        # check saved data
        notespace = NoteSpace.objects.filter(pk=1).first()
        self.assertIsNone(notespace)

    def _test_delete_notespace_denied(self):
        notespace = NoteSpace.objects.filter(pk=1).first()
        response = self.client.delete(f'/api/notespaces/{notespace.uuid}/')
        self.assertEqual(response.status_code, 403)
