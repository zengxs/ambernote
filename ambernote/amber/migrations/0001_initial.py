# Generated by Django 4.1.7 on 2023-02-16 09:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('content', models.JSONField()),
                ('revision', models.IntegerField(default=1)),
                ('is_archived', models.BooleanField(default=False)),
                ('is_pinned', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('extras', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'note',
                'verbose_name_plural': 'notes',
            },
        ),
        migrations.CreateModel(
            name='NoteLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('action', models.IntegerField(choices=[(1, 'Created'), (2, 'Updated'), (3, 'Deleted'), (4, 'Restored'), (5, 'Archived'), (6, 'Unarchived'), (7, 'Tagged'), (8, 'Untagged'), (9, 'Pinned'), (10, 'Unpinned')])),
                ('extras', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'note log',
                'verbose_name_plural': 'note logs',
            },
        ),
        migrations.CreateModel(
            name='NoteSpace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('type', models.IntegerField(choices=[(1, 'Personal'), (2, 'Team')], default=1)),
                ('name', models.CharField(max_length=255)),
                ('extras', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'note space',
                'verbose_name_plural': 'note spaces',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('extras', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notespace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='amber.notespace')),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
            },
        ),
        migrations.CreateModel(
            name='NoteSpaceMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.IntegerField(choices=[(1, 'Owner'), (2, 'Member'), (3, 'Guest')])),
                ('extras', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notespace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='amber.notespace')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='note_spaces', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'note space member',
                'verbose_name_plural': 'note space members',
            },
        ),
        migrations.AddIndex(
            model_name='notespace',
            index=models.Index(fields=['type'], name='amber_notes_type_a2980a_idx'),
        ),
        migrations.AddField(
            model_name='notelog',
            name='note',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='amber.note'),
        ),
        migrations.AddField(
            model_name='notelog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='note_logs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='note',
            name='notespace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='amber.notespace'),
        ),
        migrations.AddField(
            model_name='note',
            name='tags',
            field=models.ManyToManyField(related_name='notes', to='amber.tag'),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together={('notespace', 'name')},
        ),
        migrations.AddIndex(
            model_name='notespacemember',
            index=models.Index(fields=['role'], name='amber_notes_role_1c299a_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='notespacemember',
            unique_together={('notespace', 'user')},
        ),
        migrations.AddIndex(
            model_name='notelog',
            index=models.Index(fields=['action'], name='amber_notel_action_d29d0d_idx'),
        ),
    ]