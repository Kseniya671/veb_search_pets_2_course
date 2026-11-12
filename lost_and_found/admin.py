from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, AnimalSpecies, AnimalBreed, Location, Animal, Listing, ListingImage, Favorite
from import_export.admin import ExportActionModelAdmin
from simple_history.admin import SimpleHistoryAdmin

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone')

    @admin.display(description='Телефон')
    def get_phone(self, obj):
        return obj.profile.phone if hasattr(obj, 'profile') else '-'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class ListingInline(admin.TabularInline):
    model = Listing
    extra = 0 
    fields = ('listing_type', 'user', 'location', 'status', 'event_date')
    readonly_fields = ('user', 'event_date')
    show_change_link = True

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1

@admin.register(Animal)
class AnimalAdmin(SimpleHistoryAdmin, ExportActionModelAdmin):
    list_display = ('id', 'species', 'breed', 'sex', 'get_age_display', 'created_at')
    list_filter = ('species', 'sex', 'breed')
    search_fields = ('special_marks', 'color')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ListingInline] 

    @admin.display(description='Возраст (инфо)')
    def get_age_display(self, obj):
        return obj.age_text if obj.age_text else 'Не указан'

@admin.register(Listing)
class ListingAdmin(SimpleHistoryAdmin, ExportActionModelAdmin):
    list_display = ('id', 'listing_type', 'animal', 'location', 'user', 'status', 'get_description_short')
    list_filter = ('listing_type', 'status', 'created_at', 'location')
    search_fields = ('description', 'animal__special_marks')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'moderated_by')
    list_display_links = ('id', 'listing_type')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ListingImageInline]

    @admin.display(description='Краткое описание')
    def get_description_short(self, obj):
        return obj.description[:30] + '...' if len(obj.description) > 30 else obj.description

@admin.register(AnimalSpecies)
class AnimalSpeciesAdmin(admin.ModelAdmin):
    list_display = ('id', 'species_name')
    search_fields = ('species_name',)

@admin.register(AnimalBreed)
class AnimalBreedAdmin(admin.ModelAdmin):
    list_display = ('id', 'breed_name', 'species')
    list_filter = ('species',)
    search_fields = ('breed_name',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'region', 'district')
    list_filter = ('region',)
    search_fields = ('city', 'district')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'listing', 'added_at')
    raw_id_fields = ('user', 'listing')