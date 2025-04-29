from django.contrib import admin
from .models import Instructor, Location, Course, Section

admin.site.register(Instructor)
admin.site.register(Location)
admin.site.register(Course)
admin.site.register(Section)
