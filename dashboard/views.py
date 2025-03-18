# dashboard/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Department, MaterialRequest, Project, ProjectImage, ProjectFile, Speciality, TeamMember, Project
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from .forms import (
    AddTeamMemberForm, EditTeamMemberForm, ProfileForm, AcademicProfileForm,
    UserRegistrationForm
)


class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = "dashboard/project.html"

@ensure_csrf_cookie
@require_POST
def save_project_info(request):
    project_id = request.POST.get("project_id")
    project_progress = request.POST.get("project_progress")
    name = request.POST.get("name")
    description = request.POST.get("description")
    start_date = request.POST.get("start_date")
    deadline = request.POST.get("deadline")
    logo = request.FILES.get("logo")

    # Save or update the project information
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        project.name = name
        project.description = description
        project.start_date = start_date
        project.deadline = deadline
        project.progress = project_progress
        if logo:
            project.logo = logo
        project.save()
    else:
        project = Project.objects.create(
            name=name,
            description=description,
            start_date=start_date,
            deadline=deadline,
            logo=logo,
        )

    # Handle file uploads
    images = request.FILES.getlist("images")
    files = request.FILES.getlist("files")
    print(
        images
    )
    print(
        files
    )
    for image in images:
        if image.content_type in ["image/jpeg", "image/png", "image/gif"]:
            ProjectImage.objects.create(project=project, image=image)

    for file in files:
        if file.content_type in [
            "application/pdf",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ]:
            ProjectFile.objects.create(project=project, file=file)
    print(
        project
    )
    request.user.team_member.project = project
    request.user.team_member.save()  # Save the team_member object to update the relationship    
    print(
         request.user.team_member.project
    )

    return JsonResponse({"status": "success", "project_id": project.id})



# views.py - adding to existing file
class IndexView(LoginRequiredMixin,TemplateView):
    template_name = "dashboard/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If user is authenticated, get their projects
        if self.request.user.is_authenticated:
            if hasattr(self.request.user, 'team_member'):
                team_member = self.request.user.team_member
                if team_member.project:
                    context['project'] = team_member.project
            
            # Get recent material requests if they exist
            context['recent_materials'] = MaterialRequest.objects.filter(
                project__teammember__user=self.request.user
            ).order_by('-acquired_date')[:5]
        
        return context
    
    



@login_required
def project_view(request):
    context = {}
    
    # Get project for the current user
    if request.user.is_authenticated and hasattr(request.user, 'team_member'):
        team_member = request.user.team_member
        if team_member.project:
            context['project'] = team_member.project
            context['project_images'] = team_member.project.images.all()
            context['project_files'] = team_member.project.files.all()
    
    return render(request, 'dashboard/project.html', context)




@login_required
def team_list(request):
    """Display all team members of the current project"""
    user_team_member = get_object_or_404(TeamMember, user=request.user)
    
    # Get the project of the current user
    project = user_team_member.project
    
    if not project:
        messages.warning(request, "You are not assigned to any project.")
        return redirect('dashboard')
    
    # Get all team members for the current project
    team_members = TeamMember.objects.filter(project=project)
    
    # Initialize modals forms for inline use
    add_form = AddTeamMemberForm()
    edit_form = EditTeamMemberForm()
    
    context = {
        'team_members': team_members,
        'is_leader': user_team_member.is_project_leader,
        'project': project,
        'add_form': add_form,
        'edit_form': edit_form
    }
    
    return render(request, 'dashboard/team.html', context)

@login_required
def add_team_member(request):
    """Add a team member to the current project"""
    user_team_member = get_object_or_404(TeamMember, user=request.user)
    
    # Check if the current user is a project leader
    if not user_team_member.is_project_leader:
        return HttpResponseForbidden("You don't have permission to add team members.")
    
    # Get the project of the current user
    project = user_team_member.project
    
    if not project:
        messages.warning(request, "You are not assigned to any project.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AddTeamMemberForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            phone = form.cleaned_data['phone']
            
            # Get the user with the provided email
            user = User.objects.get(email=email)
            
            # Check if the user already has a team member profile
            try:
                team_member = TeamMember.objects.get(user=user)
                
                # Check if the team member is already in a project
                if team_member.project:
                    messages.error(request, f"{user.get_full_name()} is already assigned to a project.")
                    return redirect('team_list')
                
                # Update the team member with the new project and role
                team_member.project = project
                team_member.role = role
                team_member.phone = phone
                team_member.save()
                
            except TeamMember.DoesNotExist:
                # Create a new team member profile
                team_member = TeamMember.objects.create(
                    user=user,
                    project=project,
                    role=role,
                    phone=phone
                )
            
            messages.success(request, f"{user.get_full_name()} has been added to the team.")
            return redirect('team_list')
        else:
            # If form is invalid, return to team page with error messages
            team_members = TeamMember.objects.filter(project=project)
            edit_form = EditTeamMemberForm()
            
            context = {
                'team_members': team_members,
                'is_leader': user_team_member.is_project_leader,
                'project': project,
                'add_form': form,  # Pass the invalid form with errors
                'edit_form': edit_form
            }
            
            return render(request, 'dashboard/team.html', context)
    
    # If GET request, redirect to team list page
    return redirect('team_list')

@login_required
def edit_team_member(request, member_id):
    """Edit a team member's role and phone"""
    user_team_member = get_object_or_404(TeamMember, user=request.user)
    
    # Check if the current user is a project leader
    if not user_team_member.is_project_leader:
        return HttpResponseForbidden("You don't have permission to edit team members.")
    
    # Get the team member to edit
    member = get_object_or_404(TeamMember, id=member_id)
    
    # Check if the team member belongs to the same project as the current user
    if member.project != user_team_member.project:
        return HttpResponseForbidden("You don't have permission to edit this team member.")
    
    # Prevent editing project leaders
    if member.is_project_leader:
        messages.error(request, "You cannot edit a project leader's role.")
        return redirect('team_list')
    
    if request.method == 'POST':
        form = EditTeamMemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f"{member.user.get_full_name()}'s information has been updated.")
            return redirect('team_list')
        else:
            # If form is invalid, return to team page with error messages
            project = user_team_member.project
            team_members = TeamMember.objects.filter(project=project)
            add_form = AddTeamMemberForm()
            
            context = {
                'team_members': team_members,
                'is_leader': user_team_member.is_project_leader,
                'project': project,
                'add_form': add_form,
                'edit_form': form,  # Pass the invalid form with errors
                'edit_member_id': member_id  # Pass the ID to highlight the form
            }
            
            return render(request, 'dashboard/team.html', context)
    
    # If GET request, redirect to team list page
    return redirect('team_list')

@login_required
def remove_team_member(request, member_id):
    """Remove a team member from the project"""
    user_team_member = get_object_or_404(TeamMember, user=request.user)
    
    # Check if the current user is a project leader
    if not user_team_member.is_project_leader:
        return HttpResponseForbidden("You don't have permission to remove team members.")
    
    # Get the team member to remove
    member = get_object_or_404(TeamMember, id=member_id)
    
    # Check if the team member belongs to the same project as the current user
    if member.project != user_team_member.project:
        return HttpResponseForbidden("You don't have permission to remove this team member.")
    
    # Prevent removing project leaders
    if member.is_project_leader:
        messages.error(request, "You cannot remove a project leader from the team.")
        return redirect('team_list')
    
    # Remove the team member from the project
    member.project = None
    member.save()
    
    messages.success(request, f"{member.user.get_full_name()} has been removed from the team.")
    return redirect('team_list')

@login_required
def profile_view(request):
    """Display the current user's profile"""
    user = request.user
    team_member = get_object_or_404(TeamMember, user=user)
    project = team_member.project
    
    # Initialize forms for the modal
    profile_form = ProfileForm(instance=team_member, user=user)
    academic_form = AcademicProfileForm(instance=team_member)
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=team_member, user=user)
        academic_form = AcademicProfileForm(request.POST, instance=team_member)
        
        if profile_form.is_valid() and academic_form.is_valid():
            print(
                f"Profile updated for {user.get_full_name()}."
            )
            profile_form.save()
            academic_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('project')
    
    context = {
        'user': user,
        'team_member': team_member,
        'project': project,
        'form': profile_form,
        'academic_form': academic_form
    }
    
    return render(request, 'dashboard/profile.html', context)


# Function to handle AJAX requests to get departments based on faculty
def get_departments(request):
    """Get departments for a faculty (AJAX)"""
    faculty_id = request.GET.get('faculty')
    
    if faculty_id:
        departments = Department.objects.filter(faculty_id=faculty_id).values('id', 'latin_name')
        return JsonResponse(list(departments), safe=False)
    
    return JsonResponse([], safe=False)

# Function to handle AJAX requests to get specialities based on department
def get_specialities(request):
    """Get specialities for a department (AJAX)"""
    department_id = request.GET.get('department')
    
    if department_id:
        specialities = Speciality.objects.filter(department_id=department_id).values('id', 'latin_name')
        return JsonResponse(list(specialities), safe=False)
    
    return JsonResponse([], safe=False)

# Dashboard home view
@login_required
def dashboard_home(request):
    """Display the dashboard home page"""
    user_team_member = get_object_or_404(TeamMember, user=request.user)
    project = user_team_member.project
    
    context = {
        'user_team_member': user_team_member,
        'project': project
    }
    
    return render(request, 'dashboard/index.html', context)


def register_user(request):
    """Register a new user with a team member profile"""
        
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        team_member_form = AddTeamMemberForm(request.POST, request.FILES)
        
        if user_form.is_valid() and team_member_form.is_valid():
            # Create the user (this will also create a TeamMember via signals)
            user = user_form.save()
            
            # Get the TeamMember that was automatically created by the signal
            team_member = TeamMember.objects.get(user=user)
            
            # Update the TeamMember with form data
            team_member.project = request.user.team_member.project if hasattr(request.user, 'team_member') else None
            team_member.role = team_member_form.cleaned_data.get('role')
            team_member.phone = team_member_form.cleaned_data.get('phone')
            team_member.gender = team_member_form.cleaned_data.get('gender')
            team_member.birthday = team_member_form.cleaned_data.get('birthday')
            team_member.bio = team_member_form.cleaned_data.get('bio')
            
            # Only update photo if provided
            if 'photo' in request.FILES:
                team_member.photo = request.FILES['photo']
                
            team_member.province = team_member_form.cleaned_data.get('province')
            team_member.faculty = team_member_form.cleaned_data.get('faculty')
            team_member.department = team_member_form.cleaned_data.get('department')
            team_member.speciality = team_member_form.cleaned_data.get('speciality')
            team_member.is_project_leader = False
            team_member.is_permitted_to_demand = False
            
            team_member.save()
            
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('team_list')
    else:
        user_form = UserRegistrationForm()
        team_member_form = AddTeamMemberForm()
    
    context = {
        'user_form': user_form,
        'team_member_form': team_member_form
    }
    
    return render(request, 'registration/register.html', context)

# views.py - adding to existing file
from .models import Material, MaterialRequest

class MaterialsView(LoginRequiredMixin,TemplateView):
    template_name = "dashboard/materials.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get available materials
        context['available_materials'] = Material.objects.filter(status='available', published=True)
        
        # Get user's requested materials if authenticated
        if self.request.user.is_authenticated and hasattr(self.request.user, 'team_member'):
            team_member = self.request.user.team_member
            if team_member.project:
                context['my_materials'] = MaterialRequest.objects.filter(project=team_member.project)
                context['can_request'] = team_member.is_permitted_to_demand
                
        return context

@require_POST
def request_material(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'team_member'):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    team_member = request.user.team_member
    if not team_member.is_permitted_to_demand or not team_member.project:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    material_id = request.POST.get('material_id')
    quantity = request.POST.get('quantity', 1)
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    
    try:
        material = Material.objects.get(id=material_id, status='available', published=True)
        
        # Create material request
        material_request = MaterialRequest.objects.create(
            material=material,
            project=team_member.project,
            quantity=quantity,
            from_date=from_date,
            to_date=to_date
        )
        
        # Update material status
        material.status = 'in_use'
        material.save()
        
        return JsonResponse({'status': 'success', 'message': 'Material requested successfully'})
        
    except Material.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Material not found or not available'}, status=404)

@require_POST
def return_material(request, request_id):
    if not request.user.is_authenticated or not hasattr(request.user, 'team_member'):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    team_member = request.user.team_member
    if not team_member.is_permitted_to_demand or not team_member.project:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    try:
        # Get the material request for the current user's project
        material_request = MaterialRequest.objects.get(
            id=request_id, 
            project=team_member.project
        )
        
        # Update material status
        material = material_request.material
        material.status = 'available'
        material.save()
        
        # Delete the request
        material_request.delete()
        
        return JsonResponse({'status': 'success', 'message': 'Material returned successfully'})
        
    except MaterialRequest.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Material request not found'}, status=404)
    
    
