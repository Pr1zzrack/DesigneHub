from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError
from django.db import transaction


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name=None, password=None):
        if not email:
            raise ValueError('Поле электронной почты обязательно')
        email = self.normalize_email(email)

        with transaction.atomic():
            user = self.model(email=email, first_name=first_name, last_name=last_name)
            user.set_password(password)
            user.save(using=self._db)
            UserProfile.objects.create(user=user)

        return user

    def create_superuser(self, email, first_name, last_name=None, password=None):
        user = self.create_user(email, first_name, last_name, password)
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('premium', 'Premium'),
        ('pro', 'Pro'),
        ('standard', 'Standard'),
        ('basic', 'Basic'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='basic', blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def get_monthly_published_count(self):
        now = timezone.now()
        return self.designerwork_set.filter(publicated_date__year=now.year, publicated_date__month=now.month).count()

    def can_publish(self):
        monthly_limit = {
            'basic': 2,
            'standard': 10,
            'pro': 15,
            'premium': float('inf')
        }
        return self.get_monthly_published_count() < monthly_limit[self.status]

    def can_view(self, work):
        viewing_restrictions = {
            'basic': ['basic'],
            'standard': ['basic', 'standard'],
            'pro': ['basic', 'standard', 'pro'],
            'premium': ['basic', 'standard', 'pro', 'premium']
        }
        return work.user.status in viewing_restrictions[self.status]


class UserBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='balance')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def add_funds(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
        self.save()

    def __str__(self):
        return f"{self.user} - Balance: {self.balance}"


class Category(models.Model):
    name = models.CharField(max_length=42)

    def __str__(self):
        return self.name


class DesignerWork(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    designe_title = models.CharField(max_length=65)
    media_data = models.ImageField(upload_to='media_data/')
    descriptions = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    hashtag = models.CharField(max_length=24, verbose_name='Хэштеги')
    views = models.PositiveIntegerField(default=0, verbose_name='Счетчик просмотров')
    likes = models.PositiveIntegerField(default=0, verbose_name='Счетчик лайков')
    publicated_date = models.DateField(auto_now_add=True)
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return f'{self.user.last_name} - {self.designe_title}'

    def save(self, *args, **kwargs):
        if not self.id:
            if not self.user.can_publish():
                raise ValidationError(
                    f'Пользователь со статусом  {self.user.status} не может публиковать больше работ в этом месяце.')
        super().save(*args, **kwargs)


class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        now = timezone.now()
        return now - self.created_at < timezone.timedelta(hours=24)


class View(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    designe = models.ForeignKey(DesignerWork, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'designe')

    def __str__(self):
        return f'{self.user.last_name}'


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                related_name='user_profile')
    user_descriptions = models.TextField(blank=True, null=True)
    user_profile_image = models.ImageField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.user.first_name}'

    class UserBalance(models.Model):
        user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
        balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

        def __str__(self):
            return f'{self.user.email} - Balance: {self.balance}'

        def add_funds(self, amount):
            if amount <= 0:
                raise ValidationError("Amount to add should be positive.")
            self.balance += amount
            self.save()

        def subtract_funds(self, amount):
            if amount > self.balance:
                raise ValidationError("Insufficient funds.")
            self.balance -= amount
            self.save()

class UserSocialNetworkLink(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    social_network_title = models.CharField(max_length=32)
    link_to_social_networks = models.TextField()

    def __str__(self) -> str:
        return f'{self.user.user.first_name}'

class UserContactData(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    contact_title = models.CharField(max_length=32)
    contact_data = models.TextField()

    def __str__(self) -> str:
        return f'{self.user.user.first_name}'

class Favorite(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Пользователь')
    designs = models.ManyToManyField(DesignerWork, related_name='Избранные')

    def __str__(self):
        return f"{self.user} - {self.designs}"

class Like(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='like')
    designs = models.ManyToManyField(DesignerWork, related_name='favorites')

    def __str__(self):
        return f"{self.user} - {self.designs}"

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    design = models.ForeignKey(DesignerWork, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.design}"

class Chat(models.Model):
    user1 = models.ForeignKey(UserProfile, related_name='chats_initiated', on_delete=models.CASCADE)
    user2 = models.ForeignKey(UserProfile, related_name='chats_received', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Чат {self.user1.user.first_name} с {self.user2.user.first_name}"


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщения от {self.sender.user.first_name}, в {self.timestamp}"
