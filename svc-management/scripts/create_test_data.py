from datetime import date

from django.db import transaction
from django.contrib.auth.hashers import make_password

from management.models import (
    User,
    NutritionalProfile,
    Goal,
    NutritionalGoal,
    DietaryPreference,
    RestrictionType,
    Restriction,
)

@transaction.atomic
def create_test_data():
    # 1. Create the test user.
    user, created = User.objects.get_or_create(
        email="prueba.kora@example.com",
        defaults={
            "name": "Usuario Prueba Kora",
            "password_hash": make_password("KoraPrueba2026!"),
        },
    )

    if not created:
        user.name = "Usuario Prueba Kora"
        user.save(update_fields=["name"])

    # 2. Create the nutritional profile.
    profile, _ = NutritionalProfile.objects.get_or_create(
        user=user,
        defaults={
            "date_of_birth": date(2005, 4, 10),
            "sex": "female",
            "weight": 60.0,
            "height": 165.0,
            "activity_level": "moderate",
        },
    )

    # 3. Create the nutritional goal type.
    goal, _ = Goal.objects.get_or_create(
        name="maintenance",
        defaults={
            "description": "Mantener el peso actual",
        },
    )

    # 4. Create the active nutritional goal.
    nutritional_goal, _ = NutritionalGoal.objects.get_or_create(
        profile=profile,
        goal=goal,
        is_active=True,
        defaults={
            "calories": 2000,
            "protein": 100,
            "carbohydrates": 250,
            "fat": 65,
            "fiber": 25,
            "sugar": 50,
            "sodium": 2300,
            "start_date": date.today(),
            "end_date": date(2026, 12, 31),
        },
    )

    # 5. Create a dietary preference.
    DietaryPreference.objects.get_or_create(
        profile=profile,
        name="avena",
    )

    # 6. Create a restriction type.
    restriction_type, _ = RestrictionType.objects.get_or_create(
        name="avoid",
        defaults={
            "description": "Alimento que el usuario desea evitar",
        },
    )

    # 7. Create an avoided-food restriction.
    Restriction.objects.get_or_create(
        profile=profile,
        restriction_type=restriction_type,
        name="gluten",
    )

    # 8. Display the results.
    print("\nDatos de prueba registrados correctamente.")
    print("Usuario:", user.email)
    print("ID del usuario:", user.pk)
    print("ID del perfil nutricional:", profile.pk)
    print("ID de la meta nutricional:", nutritional_goal.pk)
    print("Preferencias:", list(
        profile.dietary_preferences.values_list("name", flat=True)
    ))
    print("Restricciones:", list(
        profile.restrictions.values_list("name", flat=True)
    ))


if __name__ == "__main__":
    create_test_data()
