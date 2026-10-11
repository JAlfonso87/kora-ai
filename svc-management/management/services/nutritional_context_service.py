
from datetime import date

from management.models import (
    NutritionalProfile,
    NutritionalGoal,
    DietaryPreference,
    Restriction,
)


def calculate_age(date_of_birth: date) -> int:
    today = date.today()

    return (
        today.year
        - date_of_birth.year
        - (
            (today.month, today.day)
            < (date_of_birth.month, date_of_birth.day)
        )
    )


def normalize_sex(value: str | None) -> str | None:
    if not value:
        return None

    normalized = value.strip().lower()

    if normalized in ("male", "masculino", "hombre"):
        return "male"

    if normalized in ("female", "femenino", "mujer"):
        return "female"

    return None


def build_nutritional_context(user):
    context = {}

    try:
        profile = user.nutritional_profile
    except NutritionalProfile.DoesNotExist:
        return context

    context["user_profile"] = {
        "age": calculate_age(profile.date_of_birth),
        "sex": normalize_sex(profile.sex),
        "weight_kg": float(profile.weight),
        "height_cm": float(profile.height),
    }

    nutritional_goal = (
        NutritionalGoal.objects
        .filter(profile=profile, is_active=True)
        .select_related("goal")
        .order_by("-start_date")
        .first()
    )

    if nutritional_goal:
        context["goals"] = {
            "primary_goal": normalize_goal(nutritional_goal.goal.name),
            "calorie_target_kcal": float(nutritional_goal.calories),
            "protein_target_g": float(nutritional_goal.protein),
        }

    preferred_foods = list(
        DietaryPreference.objects
        .filter(profile=profile)
        .values_list("name", flat=True)
    )

    context["food_preferences"] = {
        "preferred_foods": preferred_foods,
    }

    restrictions = list(
        Restriction.objects
        .filter(profile=profile)
        .select_related("restriction_type")
    )

    avoided_foods = []
    allergies = []
    unavailable_foods = []

    for restriction in restrictions:
        restriction_type = (
            restriction.restriction_type.name.strip().lower()
        )

        if "alerg" in restriction_type or "allerg" in restriction_type:
            allergies.append(restriction.name)

        elif (
            "disponibilidad" in restriction_type
            or "unavailable" in restriction_type
            or "accesibilidad" in restriction_type
        ):
            unavailable_foods.append(restriction.name)

        else:
            avoided_foods.append(restriction.name)

    context["food_restrictions"] = {
        "avoided_foods": avoided_foods,
        "unavailable_foods": unavailable_foods,
        "allergies": allergies,
    }

    return context


def normalize_goal(value: str) -> str | None:
    normalized = value.strip().lower()

    goals = {
        "weight_loss": "weight_loss",
        "pérdida de peso": "weight_loss",
        "perdida de peso": "weight_loss",
        "muscle_gain": "muscle_gain",
        "ganancia muscular": "muscle_gain",
        "maintenance": "maintenance",
        "mantenimiento": "maintenance",
    }

    return goals.get(normalized)
