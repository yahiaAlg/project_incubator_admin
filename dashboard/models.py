# models.py

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Project(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("labeled", "Labeled"),
    ]

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    progress = models.IntegerField(default=0)
    start_date = models.DateField()
    deadline = models.DateField()
    logo = models.ImageField(upload_to="project_logos/", null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )  # Add this field

    def __str__(self):
        return self.name


class Material(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("in_use", "In Use"),
    ]
    model_number = models.CharField(max_length=200, null=True, blank=True)
    manufacturer = models.CharField(max_length=200, null=True, blank=True)
    measurement_range = models.CharField(max_length=200, null=True, blank=True)
    precision = models.CharField(max_length=200, null=True, blank=True)
    power_requirements = models.CharField(max_length=200, null=True, blank=True)
    dimensions = models.CharField(max_length=200, null=True, blank=True)
    weight = models.CharField(max_length=200, null=True, blank=True)
    published = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="available"
    )

    def __str__(self):
        return self.name


class MaterialRequest(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    acquired_date = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    from_date = models.DateField(auto_now=False, auto_now_add=False)
    to_date = models.DateField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return f"{self.material.name} - {self.project.name}"


class Faculty(models.Model):

    arabic_name = models.CharField(max_length=50)
    latin_name = models.CharField(max_length=50)
    abreviated_name = models.CharField(max_length=25)

    class Meta:
        verbose_name = "faculty"
        verbose_name_plural = "faculties"

    def __str__(self):
        return self.abreviated_name

    def get_absolute_url(self):
        return reverse("faculty_detail", kwargs={"pk": self.pk})


class Department(models.Model):

    arabic_name = models.CharField(max_length=50)
    latin_name = models.CharField(max_length=50)
    abreviated_name = models.CharField(max_length=25)

    class Meta:
        verbose_name = "department"
        verbose_name_plural = "departments"

    def __str__(self):
        return self.abreviated_name

    def get_absolute_url(self):
        return reverse("department_detail", kwargs={"pk": self.pk})


class Speciality(models.Model):

    arabic_name = models.CharField(max_length=50)
    latin_name = models.CharField(max_length=50)
    abreviated_name = models.CharField(max_length=25)

    class Meta:
        verbose_name = "speciality"
        verbose_name_plural = "specialities"

    def __str__(self):
        return self.abreviated_name

    def get_absolute_url(self):
        return reverse("speciality_detail", kwargs={"pk": self.pk})


# class about provinces
class Province(models.Model):
    name = models.CharField(max_length=255)
    code = models.IntegerField(
        unique=True, blank=False, null=False, default=0, help_text="Province code", verbose_name="Province code", 
    )

    # image = models.ImageField(upload_to="province_images/%Y/%m/%d")
    def __str__(self):
        return self.name


class TeamMember(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True
    )  #
    ROLE_CHOICES = [
        ("supervisor", "Supervisor"),
        ("member", "Member"),
    ]
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    is_permitted_to_demand = models.BooleanField(default=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="team_member",
    )
    is_project_leader = models.BooleanField(default=False)
    photo = models.ImageField(
        upload_to="profiles_images/%Y/%m/%d",
        height_field=None,
        width_field=None,
        max_length=None,
    )
    phone = models.CharField(max_length=20)
    bio = models.TextField(blank=True)
    birthday = models.DateField("Date of Birth", auto_now=False, auto_now_add=False, null=True, blank=True)
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, null=True, blank=True
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.SET_NULL, null=True, blank=True
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    speciality = models.ForeignKey(
        Speciality, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.user.get_full_name()


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="project_images/%Y/%m/%d")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.project.name}"


class MaterialImage(models.Model):
    material = models.ForeignKey(
        Material, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="material_images/%Y/%m/%d")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imag"


class ProjectFile(models.Model):
    project = models.ForeignKey(Project, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to="project_files/%Y/%m/%d")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.project.name}"


class MaterialFile(models.Model):
    material = models.ForeignKey(
        Material, related_name="files", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="material_files/%Y/%m/%d")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.project.name}"


class Plan(models.Model):

    project = models.ForeignKey(Project, related_name="plans", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "plan"
        verbose_name_plural = "plans"

    def __str__(self):
        return f"Plan for {self.project.name}"

    def get_absolute_url(self):
        return reverse("plan_detail", kwargs={"pk": self.pk})


class Phase(models.Model):
    plan = models.ForeignKey(Plan, related_name="phases", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    deadline = models.DateField()

    class Meta:
        verbose_name = "phase"
        verbose_name_plural = "phases"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("phase_detail", kwargs={"pk": self.pk})


class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    phase = models.ForeignKey(Phase, related_name="tasks", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "task"
        verbose_name_plural = "tasks"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("task_detail", kwargs={"pk": self.pk})


class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    description = models.TextField()
    task = models.ForeignKey(
        Task, related_name="events", on_delete=models.SET_NULL, null=True
    )

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Event_detail", kwargs={"pk": self.pk})


class ActionUpdates(models.Model):
    action = models.CharField(max_length=50)
    done_time = models.DateTimeField()

    class Meta:
        verbose_name = "SystemActionUpdate"
        verbose_name_plural = "SystemActionUpdates"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("SystemActionUpdate_detail", kwargs={"pk": self.pk})


#  signals


from django.db.models.signals import post_save
from django.dispatch import receiver


# At the bottom of models.py, modify the signals:
@receiver(post_save, sender=User)
def create_team_member(sender, instance, created, **kwargs):
    if created:
        TeamMember.objects.create(
            user=instance,
            is_permitted_to_demand=False,
            is_project_leader=False,
            phone="",
            bio="",
            role="member",
            gender="male",
            photo="default_image_placeholder.png",  # Add a default photo
        )


@receiver(post_save, sender=User)
def save_team_member(sender, instance, **kwargs):
    if hasattr(instance, "team_member"):
        instance.team_member.save()
