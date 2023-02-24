from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.NoteSpace)
admin.site.register(models.NoteSpaceMember)
admin.site.register(models.Note)
admin.site.register(models.Tag)
admin.site.register(models.NoteLog)
