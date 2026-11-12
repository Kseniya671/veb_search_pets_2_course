from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from simple_history.models import HistoricalRecords

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Пользователь")
    display_name = models.CharField(max_length=100, blank=True, verbose_name="Отображаемое имя")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class AnimalSpecies(models.Model):
    species_name = models.CharField(max_length=100, verbose_name="Вид животного")

    class Meta:
        verbose_name = "Вид животного"
        verbose_name_plural = "Виды животных"

    def __str__(self):
        return self.species_name


class AnimalBreed(models.Model):
    species = models.ForeignKey(AnimalSpecies, on_delete=models.CASCADE, verbose_name="Вид животного")
    breed_name = models.CharField(max_length=100, verbose_name="Порода")

    class Meta:
        verbose_name = "Порода"
        verbose_name_plural = "Породы"

    def __str__(self):
        return self.breed_name


class Location(models.Model):
    region = models.CharField(max_length=100, blank=True, verbose_name="Регион")
    city = models.CharField(max_length=100, verbose_name="Город")
    district = models.CharField(max_length=100, blank=True, verbose_name="Район")

    class Meta:
        verbose_name = "Локация"
        verbose_name_plural = "Локации"

    def __str__(self):
        return f"{self.city}, {self.district}" if self.district else self.city


class Animal(models.Model):
    class Sex(models.TextChoices):
        MALE = 'M', 'Мальчик'
        FEMALE = 'F', 'Девочка'
        UNKNOWN = 'U', 'Неизвестно'
    history = HistoricalRecords()
    species = models.ForeignKey(AnimalSpecies, on_delete=models.CASCADE, verbose_name="Вид")
    breed = models.ForeignKey(AnimalBreed, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Порода")
    sex = models.CharField(max_length=1, choices=Sex.choices, default=Sex.UNKNOWN, verbose_name="Пол")
    color = models.CharField(max_length=100, blank=True, verbose_name="Окрас")
    age_text = models.CharField(max_length=100, blank=True, verbose_name="Возраст")
    special_marks = models.TextField(blank=True, verbose_name="Особые приметы")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Животное"
        verbose_name_plural = "Животные"

    def __str__(self):
        return f"{self.species} ({self.breed})"


class ActiveListingManager(models.Manager):
    def get_queryset(self):
        # Фильтруем только те объявления, у которых статус 'AC' (Активно)
        return super().get_queryset().filter(status='AC')


class Listing(models.Model):
    class ListingType(models.TextChoices):
        LOST = 'LOST', 'Потеряно'
        FOUND = 'FOUND', 'Найдено'
        
    class Status(models.TextChoices):
        ACTIVE = 'AC', 'Активно'
        ARCHIVED = 'AR', 'В архиве'
        FOUND_OWNER = 'FO', 'Хозяин найден'
    history = HistoricalRecords()
    objects = models.Manager() 
    published = ActiveListingManager() 

    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='listings', verbose_name="Животное")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', verbose_name="Автор")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="Локация")
    
    listing_type = models.CharField(max_length=10, choices=ListingType.choices, default=ListingType.LOST, verbose_name="Тип объявления")
    event_date = models.DateField(default=timezone.now, verbose_name="Дата события")
    description = models.TextField(verbose_name="Текст объявления")
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.ACTIVE, verbose_name="Статус")
    
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_listings', verbose_name="Модератор")
    moderated_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата модерации")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]

    def __str__(self):
        return f"{self.get_listing_type_display()}: {self.animal}"


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images', verbose_name="Объявление")
    file_path = models.CharField(max_length=255, verbose_name="Путь к файлу")
    file_url = models.CharField(max_length=255, blank=True, verbose_name="URL файла")
    is_primary = models.BooleanField(default=False, verbose_name="Главное фото")
    sort_order = models.IntegerField(default=0, verbose_name="Порядок сортировки")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"
        ordering = ['sort_order']

    def __str__(self):
        return f"Фото для объявления №{self.listing.id}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, verbose_name="Объявление")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = ('user', 'listing')

    def __str__(self):
        return f"{self.user.username} сохранил {self.listing.id}"