# Register your models here.
from django.contrib import admin

# PR2018-04-20
from .models import Examyear, Country, Schooldefault

admin.site.register(Examyear)
admin.site.register(Country)
admin.site.register(Schooldefault)