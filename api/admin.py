from django.contrib import admin

from .models.departments import Department
from .models.employees import Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "created_at")
    list_filter = ("parent",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "department", "hired_at")
    list_filter = ("department", "position")
