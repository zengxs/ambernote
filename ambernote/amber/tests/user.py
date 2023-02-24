from django.test import TestCase
from rest_framework.test import APIClient

from ambernote.authx.models import User


class UserTestCase(TestCase):
    fixtures = (
        'testdata-1.yaml',
    )

    def setUp(self):
        self.client = APIClient()

    def test_admin(self):
        self.client.force_login(User.objects.filter(pk=1).get())  # as admin
        self._test_list_user_success()
        self._test_read_user_success(1)  # read self
        self._test_read_user_success(2)  # read other user
        self._test_update_user_success(1)  # update self
        self._test_update_user_success(2)  # update other user
        self._test_add_user_not_allowed()
        self._test_delete_user_not_allowed(3)

    def test_not_admin(self):
        self.client.force_login(User.objects.filter(pk=2).get())  # not admin
        self._test_list_user_denied()
        self._test_read_user_success(2)  # read self
        self._test_read_user_denied(1)  # read other user
        self._test_update_user_success(2)  # update self
        self._test_update_user_denied(3)  # update other user

    def test_anonymous(self):
        # not login
        self._test_list_user_denied()
        self._test_read_user_denied(2)
        self._test_update_user_denied(2)

    def _test_read_user_success(self, user_pk: int):
        user = User.objects.filter(pk=user_pk).get()
        response = self.client.get(f'/api/users/{user.uuid}/')
        self.assertEqual(response.status_code, 200)  # OK

    def _test_read_user_denied(self, user_pk: int):
        user = User.objects.filter(pk=user_pk).get()
        response = self.client.get(f'/api/users/{user.uuid}/')
        self.assertEqual(response.status_code, 403)

    def _test_list_user_success(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 200)

    def _test_list_user_denied(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 403)

    def _test_update_user_success(self, user_pk: int):
        user = User.objects.filter(pk=user_pk).get()
        data = {
            'fullname': 'new name',
        }
        response = self.client.put(f'/api/users/{user.uuid}/', data=data)
        self.assertEqual(response.status_code, 200)

        # check updated data
        user.refresh_from_db()
        self.assertEqual(user.fullname, data['fullname'])

    def _test_update_user_denied(self, user_pk: int):
        user = User.objects.filter(pk=user_pk).get()
        data = {
            'fullname': 'new name',
        }
        response = self.client.put(f'/api/users/{user.uuid}/', data=data)
        self.assertEqual(response.status_code, 403)

        # check not updated
        user.refresh_from_db()
        self.assertNotEqual(user.fullname, data['fullname'])

    def _test_add_user_not_allowed(self):
        response = self.client.post('/api/users/', data={})
        self.assertEqual(response.status_code, 405)

    def _test_delete_user_not_allowed(self, user_pk: int):
        user = User.objects.filter(pk=user_pk).get()
        response = self.client.delete(f'/api/users/{user.uuid}/')
        self.assertEqual(response.status_code, 405)
