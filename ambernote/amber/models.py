import logging
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class NoteSpace(models.Model):
    """Note space model"""

    class Meta:
        verbose_name = _('note space')
        verbose_name_plural = _('note spaces')

        indexes = [
            models.Index(fields=['type']),
        ]

    class Type(models.IntegerChoices):
        PERSONAL = 1, _('Personal')
        TEAM = 2, _('Team')

    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    type = models.IntegerField(choices=Type.choices, default=Type.PERSONAL)
    name = models.CharField(max_length=255)
    extras = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        choices_map = dict(self.Type.choices)  # convert choices to dict
        type_name = choices_map[self.type]
        return f'{self.name} ({type_name})'


class NoteSpaceMember(models.Model):
    """Note space member model"""

    class Meta:
        verbose_name = _('note space member')
        verbose_name_plural = _('note space members')

        unique_together = ('notespace', 'user')
        indexes = [
            models.Index(fields=['role']),
        ]

    class Role(models.IntegerChoices):
        OWNER = 1, _('Owner')  # read-write notes and manage space
        MEMBER = 2, _('Member')  # read-write notes
        GUEST = 3, _('Guest')  # read-only

    notespace = models.ForeignKey(NoteSpace, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='note_spaces')
    role = models.IntegerField(choices=Role.choices)
    extras = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} ({self.notespace})'


class Tag(models.Model):
    """Note tag model"""

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

        unique_together = ('notespace', 'name')

    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    notespace = models.ForeignKey(NoteSpace, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=255)
    extras = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Note(models.Model):
    """Note model"""

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')

    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    title = models.CharField(max_length=255, blank=True)
    content = models.JSONField()

    # Incremented when the note's "contents" is changed (title and content)
    # May be used to detect conflicts
    revision = models.IntegerField(default=1)

    is_archived = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # In the trash, not deleted permanently

    notespace = models.ForeignKey(NoteSpace, on_delete=models.CASCADE, related_name='notes')
    tags = models.ManyToManyField(Tag, related_name='notes')
    extras = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return f'Untitled ({self.uuid})'

    def save(self, *args, **kwargs):
        # increment revision if title or content is changed
        rev_increment = False
        if self.pk:  # if the note already exists
            original = Note.objects.get(pk=self.pk)
            if original.title != self.title or original.content != self.content:
                rev_increment = True
                self.revision += 1

        super().save(*args, **kwargs)

        if rev_increment:
            logger.debug(f'Note {self.uuid} revision incremented to {self.revision}')


class NoteLog(models.Model):
    """Note log model"""

    class Meta:
        verbose_name = _('note log')
        verbose_name_plural = _('note logs')

        indexes = [
            models.Index(fields=['action']),
        ]

    class Action(models.IntegerChoices):
        CREATED = 1, _('Created')
        UPDATED = 2, _('Updated')
        DELETED = 3, _('Deleted')  # Moved to trash
        RESTORED = 4, _('Restored')  # Restored from trash
        ARCHIVED = 5, _('Archived')
        UNARCHIVED = 6, _('Unarchived')
        TAGGED = 7, _('Tagged')
        UNTAGGED = 8, _('Untagged')
        PINNED = 9, _('Pinned')
        UNPINNED = 10, _('Unpinned')

    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='note_logs')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='logs')
    action = models.IntegerField(choices=Action.choices)
    extras = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.action} ({self.note})'
