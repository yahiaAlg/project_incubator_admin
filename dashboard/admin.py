# admin.py

from django.contrib import admin
from .models import (
    Project, Material, MaterialRequest, Faculty, Department, Speciality,
    Province, TeamMember, ProjectImage, MaterialImage, ProjectFile,
    MaterialFile, Plan, Phase, Task, Event, ActionUpdates
)

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 1

class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'deadline', 'status', 'progress')
    list_filter = ('status', 'start_date')
    search_fields = ('name', 'description')
    inlines = [ProjectImageInline, ProjectFileInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'status')
        }),
        ('Timeline', {
            'fields': ('start_date', 'deadline', 'progress')
        }),
        ('Media', {
            'fields': ('logo',),
            'classes': ('collapse',)
        }),
    )

class MaterialImageInline(admin.TabularInline):
    model = MaterialImage
    extra = 1

class MaterialFileInline(admin.TabularInline):
    model = MaterialFile
    extra = 1

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_number', 'manufacturer', 'status', 'published')
    list_filter = ('status', 'published', 'manufacturer')
    search_fields = ('name', 'description', 'model_number')
    inlines = [MaterialImageInline, MaterialFileInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'status', 'published')
        }),
        ('Specifications', {
            'fields': ('model_number', 'manufacturer', 'measurement_range', 'precision',
                      'power_requirements', 'dimensions', 'weight')
        }),
    )

@admin.register(MaterialRequest)
class MaterialRequestAdmin(admin.ModelAdmin):
    list_display = ('material', 'project', 'quantity', 'acquired_date', 'from_date', 'to_date')
    list_filter = ('acquired_date', 'from_date', 'to_date')
    search_fields = ('material__name', 'project__name')
    autocomplete_fields = ['material', 'project']

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('abreviated_name', 'latin_name', 'arabic_name')
    search_fields = ('latin_name', 'arabic_name', 'abreviated_name')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('abreviated_name', 'latin_name', 'arabic_name')
    search_fields = ('latin_name', 'arabic_name', 'abreviated_name')

@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ('abreviated_name', 'latin_name', 'arabic_name')
    search_fields = ('latin_name', 'arabic_name', 'abreviated_name')

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name',)
    list_filter = ('code',)

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'is_project_leader', 'is_permitted_to_demand')
    list_filter = ('role', 'gender', 'is_project_leader', 'is_permitted_to_demand', 'faculty', 'department')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    autocomplete_fields = ['user', 'project', 'faculty', 'department', 'speciality', 'province']
    fieldsets = (
        (None, {
            'fields': ('user', 'role', 'gender', 'photo')
        }),
        ('Project Information', {
            'fields': ('project', 'is_project_leader', 'is_permitted_to_demand')
        }),
        ('Personal Information', {
            'fields': ('phone', 'birthday', 'province', 'bio')
        }),
        ('Academic Information', {
            'fields': ('faculty', 'department', 'speciality')
        }),
    )

class PhaseInline(admin.TabularInline):
    model = Phase
    extra = 1

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('project',)
    search_fields = ('project__name',)
    autocomplete_fields = ['project']
    inlines = [PhaseInline]

class TaskInline(admin.TabularInline):
    model = Task
    extra = 1

@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'plan', 'deadline')
    list_filter = ('deadline',)
    search_fields = ('title', 'plan__project__name')
    autocomplete_fields = ['plan']
    inlines = [TaskInline]

class EventInline(admin.TabularInline):
    model = Event
    extra = 1

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'phase')
    search_fields = ('name', 'description', 'phase__title')
    autocomplete_fields = ['phase']
    inlines = [EventInline]

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'task')
    list_filter = ('date',)
    search_fields = ('name', 'description')
    autocomplete_fields = ['task']

@admin.register(ActionUpdates)
class ActionUpdatesAdmin(admin.ModelAdmin):
    list_display = ('action', 'done_time')
    list_filter = ('done_time',)
    search_fields = ('action',)

# Register the remaining models if any weren't already registered with a custom admin class
admin.site.register(ProjectImage)
admin.site.register(MaterialImage)
admin.site.register(ProjectFile)
admin.site.register(MaterialFile)