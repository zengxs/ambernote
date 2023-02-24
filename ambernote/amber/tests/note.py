from django.test import TestCase
from rest_framework.test import APIClient

from ambernote.amber.models import Note, NoteLog, NoteSpace
from ambernote.authx.models import User


class NoteTestCase(TestCase):
    fixtures = (
        'testdata-1.yaml',
    )

    def setUp(self):
        self.client = APIClient()

    def test_admin(self):
        self.client.force_login(User.objects.filter(pk=1).first())  # as admin
        self._test_add_note_success()
        self._test_change_flags_success()
        self._test_update_note_success()
        self._test_read_note_success()
        self._test_destroy_note_success()

    def test_owner(self):
        self.client.force_login(User.objects.filter(pk=2).first())  # as owner
        self._test_add_note_success()
        self._test_change_flags_success()
        self._test_update_note_success()
        self._test_read_note_success()
        self._test_destroy_note_denied()

    def test_member(self):
        self.client.force_login(User.objects.filter(pk=3).first())  # as member
        self._test_add_note_success()
        self._test_change_flags_success()
        self._test_update_note_success()
        self._test_read_note_success()
        self._test_destroy_note_denied()

    def test_guest(self):
        self.client.force_login(User.objects.filter(pk=4).first())  # as guest
        self._test_add_note_denied()
        self._test_change_flags_denied()
        self._test_update_note_denied()
        self._test_read_note_success()
        self._test_destroy_note_denied()

    def test_other_user(self):
        self.client.force_login(User.objects.filter(pk=5).first())  # user not belong to notespace
        self._test_add_note_denied()
        self._test_change_flags_denied()
        self._test_update_note_denied()
        self._test_read_note_denied()
        self._test_destroy_note_denied()

    def test_anonymous(self):
        self._test_add_note_denied()
        self._test_change_flags_denied()
        self._test_update_note_denied()
        self._test_read_note_denied()
        self._test_destroy_note_denied()

    def _test_add_note_success(self):
        data = {
            'notespace': NoteSpace.objects.filter(pk=1).first().uuid,
            'title': 'test add note',
            'content': {},
        }
        response = self.client.post('/api/notes/', data=data, format='json')
        self.assertEqual(response.status_code, 201)

        # check saved data
        note = Note.objects.filter(notespace__uuid=data['notespace']).order_by('-created_at').first()
        self.assertIsNotNone(note)
        self.assertEqual(note.title, data['title'])
        self.assertEqual(note.content, data['content'])

        self.assertEqual(note.logs.count(), 1)
        log = note.logs.first()
        self.assertEqual(log.action, NoteLog.Action.CREATED)

    def _test_add_note_denied(self):
        data = {
            'notespace': NoteSpace.objects.filter(pk=1).first().uuid,
            'title': 'test add note',
            'content': {},
        }
        response = self.client.post('/api/notes/', data=data, format='json')
        self.assertEqual(response.status_code, 403)

    def _test_change_flags_success(self):
        note = Note.objects.filter(pk=1).first()

        def _test_flag(path, flag_name, flag_value, expected_action):
            response = self.client.post(f'/api/notes/{note.uuid}/{path}')
            self.assertEqual(response.status_code, 200)

            # check saved data
            note.refresh_from_db()
            self.assertEqual(getattr(note, flag_name), flag_value)

            # check log
            log = note.logs.order_by('-created_at').first()
            self.assertEqual(log.action, expected_action)

        _test_flag('archive/', 'is_archived', True, NoteLog.Action.ARCHIVED)
        _test_flag('unarchive/', 'is_archived', False, NoteLog.Action.UNARCHIVED)
        _test_flag('pin/', 'is_pinned', True, NoteLog.Action.PINNED)
        _test_flag('unpin/', 'is_pinned', False, NoteLog.Action.UNPINNED)
        _test_flag('delete/', 'is_deleted', True, NoteLog.Action.DELETED)
        _test_flag('restore/', 'is_deleted', False, NoteLog.Action.RESTORED)

    def _test_change_flags_denied(self):
        note = Note.objects.filter(pk=1).get()

        def _test_flag_denied(path):
            response = self.client.post(f'/api/notes/{note.uuid}/{path}')
            self.assertEqual(response.status_code, 403)

        _test_flag_denied('archive/')
        _test_flag_denied('unarchive/')
        _test_flag_denied('pin/')
        _test_flag_denied('unpin/')
        _test_flag_denied('delete/')
        _test_flag_denied('restore/')

    def _test_update_note_success(self):
        note = Note.objects.filter(pk=1).first()
        old_title = note.title
        old_content = note.content

        data = {
            'title': 'test update note',
            'content': {
                "type": "doc",
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": "test update note"}]}],
            },
        }
        response = self.client.patch(f'/api/notes/{note.uuid}/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

        # check saved data
        note.refresh_from_db()
        self.assertEqual(note.title, data['title'])
        self.assertEqual(note.content, data['content'])

        # check log
        log = note.logs.order_by('-created_at').first()
        self.assertEqual(log.action, NoteLog.Action.UPDATED)
        self.assertEqual(log.extras['old']['title'], old_title)
        self.assertEqual(log.extras['old']['content'], old_content)
        self.assertEqual(log.extras['new']['title'], data['title'])
        self.assertEqual(log.extras['new']['content'], data['content'])

    def _test_update_note_denied(self):
        note = Note.objects.filter(pk=1).first()
        data = {
            'title': 'test update note',
            'content': {
                "type": "doc",
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": "test update note"}]}],
            },
        }
        response = self.client.patch(f'/api/notes/{note.uuid}/', data=data, format='json')
        self.assertEqual(response.status_code, 403)

    def _test_read_note_success(self):
        note = Note.objects.filter(pk=1).first()
        response = self.client.get(f'/api/notes/{note.uuid}/')
        self.assertEqual(response.status_code, 200)

    def _test_read_note_denied(self):
        note = Note.objects.filter(pk=1).first()
        response = self.client.get(f'/api/notes/{note.uuid}/')
        self.assertEqual(response.status_code, 403)

    def _test_destroy_note_success(self):
        """
        Really delete note, not just mark as deleted
        Only admin can do this
        """
        note = Note.objects.filter(pk=1).first()
        note_uuid = note.uuid
        response = self.client.delete(f'/api/notes/{note.uuid}/')
        self.assertEqual(response.status_code, 204)

        # check saved data
        with self.assertRaises(Note.DoesNotExist):
            note.refresh_from_db()

        # check log (should be deleted cascade)
        log = NoteLog.objects.filter(note__uuid=note_uuid).order_by('-created_at')
        self.assertEqual(log.count(), 0)

    def _test_destroy_note_denied(self):
        note = Note.objects.filter(pk=1).first()
        response = self.client.delete(f'/api/notes/{note.uuid}/')
        self.assertEqual(response.status_code, 403)
