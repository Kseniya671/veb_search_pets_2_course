from django.core.management.base import BaseCommand
from faker import Faker
from lost_and_found.models import AnimalSpecies, AnimalBreed, Location, Animal, Listing
from django.contrib.auth.models import User
import random

class Command(BaseCommand):
    help = 'Заполняет базу фейковыми данными'

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')
        
        species_breeds = {
            'Собака': ['Овчарка', 'Лабрадор', 'Хаски', 'Корги', 'Терьер', 'Пудель'],
            'Кошка': ['Британская', 'Сфинкс', 'Мейн-кун', 'Бенгальская', 'Персидская', 'Дворовая'],
            'Попугай': ['Ара', 'Какаду', 'Волнистый', 'Жако', 'Корелла'],
            'Грызун': ['Хомяк', 'Крыса', 'Морская свинка', 'Шиншилла', 'Хорек']
        }

        for species_name, breeds_list in species_breeds.items():
            species, _ = AnimalSpecies.objects.get_or_create(species_name=species_name)
            for breed_name in breeds_list:
                AnimalBreed.objects.get_or_create(
                    species=species, 
                    breed_name=breed_name
                )

        for _ in range(10):
            Location.objects.get_or_create(
                region=fake.region(),
                city=fake.city(),
                district=fake.street_name()
            )

        user, _ = User.objects.get_or_create(username='testuser')

        species_list = AnimalSpecies.objects.all()
        breeds = AnimalBreed.objects.all()
        locations = Location.objects.all()

        marks_list = [
            "Ошейник красного цвета", 
            "Без ошейника", 
            "Хромает на левую лапу", 
            "На шее бант", 
            "Очень худая", 
            "Пушистый хвост", 
            "Есть шрам на ухе",
            "Очень дружелюбный"
        ]

        description_templates = [
            "Пропал {} около метро. Очень пугливый, просьба позвонить, если увидите.",
            "Найден {} на улице. Ищу старых или новых хозяев.",
            "Потерялся {} в районе парка. Отзывается на кличку.",
            "Заметил {} во дворе. Выглядит потерявшимся, но в руки не идет.",
            "Срочно ищу хозяев для {}. Сидит на остановке и плачет."
        ]

        for _ in range(50):
            chosen_species = random.choice(species_list)
            chosen_breed = random.choice(breeds.filter(species=chosen_species))
            
            animal = Animal.objects.create(
                species=chosen_species,
                breed=chosen_breed,
                sex=random.choice(['M', 'F', 'U']),
                color=fake.color_name(),
                age_text=f"{random.randint(1, 10)} лет",
                special_marks=random.choice(marks_list)
            )
            
            description_text = random.choice(description_templates).format(chosen_species.species_name.lower())
            
            Listing.objects.create(
                animal=animal,
                user=user,
                location=random.choice(locations),
                listing_type=random.choice(['LOST', 'FOUND']),
                description=description_text,
                status='AC'
            )
        self.stdout.write(self.style.SUCCESS('База успешно заполнена 50 объявлениями!'))