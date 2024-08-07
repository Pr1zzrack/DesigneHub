# Generated by Django 5.0.6 on 2024-08-06 14:30

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=42)),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(blank=True, max_length=30, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(blank=True, choices=[('premium', 'Premium'), ('pro', 'Pro'), ('standard', 'Standard'), ('basic', 'Basic')], default='basic', max_length=10, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DesignerWork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designe_title', models.CharField(max_length=65)),
                ('media_data', models.ImageField(upload_to='media_data/')),
                ('descriptions', models.TextField(blank=True, null=True)),
                ('hashtag', models.CharField(max_length=24, verbose_name='Хэштеги')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='Счетчик просмотров')),
                ('likes', models.PositiveIntegerField(default=0, verbose_name='Счетчик лайков')),
                ('publicated_date', models.DateField(auto_now_add=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], default='draft', max_length=10)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DesignerHubApp.category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='user_profile_id', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('user_descriptions', models.TextField(blank=True, null=True)),
                ('user_profile_image', models.ImageField(blank=True, null=True, upload_to='')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PasswordResetToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designs', models.ManyToManyField(related_name='favorites', to='DesignerHubApp.designerwork')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='like', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designs', models.ManyToManyField(related_name='Избранные', to='DesignerHubApp.designerwork')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='Пользователь', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserSocialNetworkLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social_network_title', models.CharField(max_length=32)),
                ('link_to_social_networks', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DesignerHubApp.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='UserContactData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_title', models.CharField(max_length=32)),
                ('contact_data', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DesignerHubApp.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='DesignerHubApp.chat')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DesignerHubApp.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='DesigneWorkReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('design', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DesignerHubApp.designerwork')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DesignerHubApp.userprofile')),
            ],
        ),
        migrations.AddField(
            model_name='chat',
            name='user1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats_initiated', to='DesignerHubApp.userprofile'),
        ),
        migrations.AddField(
            model_name='chat',
            name='user2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats_received', to='DesignerHubApp.userprofile'),
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('designe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DesignerHubApp.designerwork')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'designe')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='chat',
            unique_together={('user1', 'user2')},
        ),
    ]
