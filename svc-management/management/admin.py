from django.contrib import admin

from .models import (
    User,
    NutritionalProfile,
    MedicalCondition,
    DietaryPreference,
    RestrictionType,
    Restriction,
    Goal,
    NutritionalGoal,
    Conversation,
    Message,
    AuditLog,
)


admin.site.register(User)
admin.site.register(NutritionalProfile)
admin.site.register(MedicalCondition)
admin.site.register(DietaryPreference)
admin.site.register(RestrictionType)
admin.site.register(Restriction)
admin.site.register(Goal)
admin.site.register(NutritionalGoal)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(AuditLog)