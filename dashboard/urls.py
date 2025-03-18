# urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    # Page views
    path('', views.IndexView.as_view(), name='index'),
    path('project/', views.project_view, name='project'),
    path('team/', views.team_list, name='team_list'),  # Changed to match function-based view
    path('materials/', views.MaterialsView.as_view(), name='materials'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_home, name='dashboard'),  # Added missing dashboard route
    path('register/', views.register_user, name='register'),  # Added register route
    
    # Academic dropdown data endpoints
    path('api/get-departments/', views.get_departments, name='get_departments'),
    path('api/get-specialities/', views.get_specialities, name='get_specialities'),
    
    # API endpoints
    path('api/save-project/', views.save_project_info, name='save_project_info'),
    path('api/add-team-member/', views.add_team_member, name='add_team_member'),
    path('api/edit-team-member/<int:member_id>/', views.edit_team_member, name='edit_team_member'),  # Fixed to match view
    path('api/remove-team-member/<int:member_id>/', views.remove_team_member, name='remove_team_member'),
    path('api/request-material/', views.request_material, name='request_material'),
    path('api/return-material/<int:request_id>/', views.return_material, name='return_material'),
    
    # Auth views
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]