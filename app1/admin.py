from django.contrib import admin
from .models import (
    User,
    Category,
    Quiz,
    Question,
    Choice,
    UserAnswer,
    Score,
)

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Quiz)
admin.site.register(Choice)
admin.site.register(UserAnswer)
admin.site.register(Score)
