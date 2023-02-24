from django.test import TestCase
from rest_framework.test import APIClient

from ambernote.amber.models import NoteSpace, Tag
from ambernote.authx.models import User


class TagTestCase(TestCase):
    fixtures = (
        'testdata-1.yaml',
    )

    def setUp(self):
        self.client = APIClient()

    def test_admin(self):
        self.client.force_login(User.objects.filter(pk=1).first())  # as admin
        self._test_add_tag_success()
        self._test_read_tag_success()
        self._test_list_tags_success()
        self._test_delete_tag_success()

    def test_owner(self):
        self.client.force_login(User.objects.filter(pk=2).first())  # as owner
        self._test_add_tag_success()
        self._test_read_tag_success()
        self._test_list_tags_success()
        self._test_delete_tag_success()

    def test_member(self):
        self.client.force_login(User.objects.filter(pk=3).first())  # as member
        self._test_add_tag_success()
        self._test_read_tag_success()
        self._test_list_tags_success()
        self._test_delete_tag_success()

    def test_guest(self):
        self.client.force_login(User.objects.filter(pk=4).first())  # as guest
        self._test_add_tag_denied()
        self._test_read_tag_success()
        self._test_list_tags_success()
        self._test_delete_tag_denied()

    def test_other_user(self):
        self.client.force_login(User.objects.filter(pk=5).first())  # not belong to notespace
        self._test_add_tag_denied()
        self._test_read_tag_denied()
        self._test_list_tags_denied()
        self._test_delete_tag_denied()

    def _test_add_tag_success(self):
        data = {
            'name': 'test tag',
            'notespace': NoteSpace.objects.filter(pk=1).first().uuid,
        }
        response = self.client.post('/api/tags/', data=data)
        self.assertEqual(response.status_code, 201)

        # check saved data
        tag = Tag.objects.filter(
            name=data['name'],
            notespace__uuid=data['notespace'],
        ).first()
        self.assertIsNotNone(tag)

    def _test_add_tag_denied(self):
        data = {
            'name': 'test tag',
            'notespace': NoteSpace.objects.filter(pk=1).first().uuid,
        }
        response = self.client.post('/api/tags/', data=data)
        self.assertEqual(response.status_code, 403)

    def _test_read_tag_success(self):
        tag = Tag.objects.filter(pk=1).first()
        response = self.client.get(f'/api/tags/{tag.uuid}/')
        self.assertEqual(response.status_code, 200)

    def _test_read_tag_denied(self):
        tag = Tag.objects.filter(pk=1).first()
        response = self.client.get(f'/api/tags/{tag.uuid}/')
        self.assertEqual(response.status_code, 403)

    def _test_list_tags_success(self):
        notespace = NoteSpace.objects.filter(pk=1).first()
        response = self.client.get('/api/tags/', data={'notespace': notespace.uuid})
        self.assertEqual(response.status_code, 200)

    def _test_list_tags_denied(self):
        notespace = NoteSpace.objects.filter(pk=1).first()
        response = self.client.get('/api/tags/', data={'notespace': notespace.uuid})
        self.assertEqual(response.status_code, 403)

    def _test_delete_tag_success(self):
        tag = Tag.objects.filter(pk=1).first()
        response = self.client.delete(f'/api/tags/{tag.uuid}/')
        self.assertEqual(response.status_code, 204)

    def _test_delete_tag_denied(self):
        tag = Tag.objects.filter(pk=1).first()
        response = self.client.delete(f'/api/tags/{tag.uuid}/')
        self.assertEqual(response.status_code, 403)
