# Register your models here.
from django.contrib import admin

# PR2018-07-20
from .models import Subjectdefault, Subject

admin.site.register(Subjectdefault)
admin.site.register(Subject)