#!/bin/bash

# Define the project and app names
PROJECT_NAME="project_dashboard"
APP_NAME="dashboard"




# Create a new Django project
django-admin startproject $PROJECT_NAME .

# Create a new Django app
python manage.py startapp $APP_NAME

# Create the necessary directories for static and template files
mkdir -p $APP_NAME/static/$APP_NAME/js
mkdir -p $APP_NAME/templates/$APP_NAME

# Create the JavaScript file for drag and drop functionality
JS_FILE="$APP_NAME/static/$APP_NAME/js/drag_and_drop_upload.js"
cat << 'EOF' > "$JS_FILE"
document.addEventListener('DOMContentLoaded', function() {
    const imageUploadArea = document.querySelector('.dropzone-area');
    const fileUploadArea = document.querySelectorAll('.dropzone-area')[1];

    if (imageUploadArea) {
        initDropArea(imageUploadArea,
                    ['image/jpeg', 'image/png', 'image/gif'],
                    '/api/project/upload-images/');
    }

    if (fileUploadArea) {
        initDropArea(fileUploadArea,
                    ['application/pdf', 'application/vnd.ms-powerpoint',
                     'application/vnd.openxmlformats-officedocument.presentationml.presentation'],
                    '/api/project/upload-files/');
    }

    function initDropArea(element, allowedTypes, apiEndpoint) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            element.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            element.addEventListener(eventName, () => {
                element.classList.add('drag-highlight');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            element.addEventListener(eventName, () => {
                element.classList.remove('drag-highlight');
            });
        });

        element.addEventListener('drop', handleDrop);

        element.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.multiple = true;

            if (allowedTypes.includes('image/jpeg')) {
                input.accept = 'image/*';
            } else if (allowedTypes.includes('application/pdf')) {
                input.accept = '.pdf,.ppt,.pptx';
            }

            input.onchange = e => handleFiles(e.target.files);
            input.click();
        });

        function handleDrop(e) {
            const files = e.dataTransfer.files;
            handleFiles(files);
        }

        function handleFiles(files) {
            const fileArray = [...files];
            const validFiles = fileArray.filter(file => {
                return allowedTypes.some(type => file.type.match(type));
            });

            if (validFiles.length === 0) {
                showMessage(element, 'No valid files selected. Please upload the correct file type.');
                return;
            }

            validFiles.forEach(file => uploadFile(file, element, apiEndpoint));
        }

        function uploadFile(file, element, url) {
            const formData = new FormData();
            formData.append('file', file);
            const csrftoken = getCookie('csrftoken');

            const progressContainer = document.createElement('div');
            progressContainer.className = 'upload-progress';
            progressContainer.innerHTML = `
                <span>${file.name}</span>
                <div class="progress-bar-container">
                    <div class="progress-bar"></div>
                </div>
                <span class="percent">0%</span>
            `;
            element.appendChild(progressContainer);

            const progressBar = progressContainer.querySelector('.progress-bar');
            const percentText = progressContainer.querySelector('.percent');

            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', function(e) {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    progressBar.style.width = percent + '%';
                    percentText.textContent = percent + '%';
                }
            });

            xhr.addEventListener('load', function() {
                if (xhr.status >= 200 && xhr.status < 300) {
                    progressContainer.remove();
                    showMessage(element, `Successfully uploaded: ${file.name}`, 'success');
                    try {
                        const response = JSON.parse(xhr.responseText);
                        console.log('File uploaded:', response);
                    } catch (e) {
                        console.error('Error parsing server response');
                    }
                } else {
                    progressContainer.remove();
                    showMessage(element, `Upload failed: ${xhr.statusText || 'Server error'}`, 'error');
                }
            });

            xhr.addEventListener('error', function() {
                progressContainer.remove();
                showMessage(element, `Network error uploading: ${file.name}`, 'error');
            });

            xhr.open('POST', url, true);
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
            xhr.send(formData);
        }

        function showMessage(element, message, type = 'info') {
            const msgElement = document.createElement('div');
            msgElement.className = `upload-message ${type}`;
            msgElement.textContent = message;
            element.appendChild(msgElement);
            setTimeout(() => msgElement.remove(), 5000);
        }

        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    }

    const style = document.createElement('style');
    style.textContent = `
        .drag-highlight {
            border: 2px dashed #4285f4 !important;
            background-color: rgba(66, 133, 244, 0.1) !important;
        }
        .upload-progress {
            margin: 10px 0;
            padding: 8px;
            background: #f5f5f5;
            border-radius: 4px;
            display: flex;
            align-items: center;
        }
        .progress-bar-container {
            flex: 1;
            height: 10px;
            background: #e0e0e0;
            border-radius: 5px;
            margin: 0 10px;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background: #4285f4;
            width: 0%;
            transition: width 0.2s;
        }
        .upload-message {
            padding: 10px;
            margin: 8px 0;
            border-radius: 4px;
        }
        .upload-message.success {
            background: #e6f4ea;
            color: #137333;
        }
        .upload-message.error {
            background: #fce8e6;
            color: #c5221f;
        }
    `;
    document.head.appendChild(style);
});
EOF

# Create the Django view for handling file uploads
VIEW_FILE="$APP_NAME/views.py"
cat << 'EOF' > "$VIEW_FILE"
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
import os
from django.conf import settings
import uuid

@ensure_csrf_cookie
@require_POST
def upload_project_files(request, file_type):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    file = request.FILES['file']

    if file_type == 'images':
        valid_types = ['image/jpeg', 'image/png', 'image/gif']
        folder = 'project_images'
    else:
        valid_types = ['application/pdf', 'application/vnd.ms-powerpoint',
                      'application/vnd.openxmlformats-officedocument.presentationml.presentation']
        folder = 'project_files'

    if file.content_type not in valid_types:
        return JsonResponse({'error': 'Invalid file type'}, status=400)

    unique_filename = f"{uuid.uuid4().hex}_{file.name}"
    save_dir = os.path.join(settings.MEDIA_ROOT, folder)
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, unique_filename)

    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    file_url = f"{settings.MEDIA_URL}{folder}/{unique_filename}"

    return JsonResponse({
        'status': 'success',
        'file_url': file_url,
        'filename': unique_filename
    })
EOF

# Update the URL configuration
URLS_FILE="$APP_NAME/urls.py"
cat << 'EOF' > "$URLS_FILE"
from django.urls import path
from . import views

urlpatterns = [
    path('api/project/upload-images/', views.upload_project_files, {'file_type': 'images'}, name='upload_images'),
    path('api/project/upload-files/', views.upload_project_files, {'file_type': 'files'}, name='upload_files'),
]
EOF

# Create the HTML template file
TEMPLATE_FILE="$APP_NAME/templates/$APP_NAME/project.html"
cat << 'EOF' > "$TEMPLATE_FILE"
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Project - Project Dashboard</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css"
      rel="stylesheet"
    />
    <link href="{% static 'dashboard/js/drag_and_drop_upload.js' %}" rel="stylesheet" />
  </head>
  <body>
    <header class="bg-primary text-white p-3">
      <div class="container d-flex justify-content-between align-items-center">
        <h1 class="h3 mb-0">Project Dashboard</h1>
        <a href="logout.html" class="btn btn-light btn-sm">
          <i class="bi bi-box-arrow-right me-1"></i> Logout
        </a>
      </div>
    </header>

    <div class="container mt-4">
      <!-- Navigation Menu -->
      <nav class="nav nav-pills nav-fill mb-4">
        <a class="nav-link" href="profile.html">
          <i class="bi bi-person me-2"></i>Profile
        </a>
        <a class="nav-link" href="materials.html">
          <i class="bi bi-box me-2"></i>Materials
        </a>
        <a class="nav-link" href="team.html">
          <i class="bi bi-people me-2"></i>Team
        </a>
        <a class="nav-link active" href="project.html">
          <i class="bi bi-clipboard-data me-2"></i>Project
        </a>
      </nav>

      <!-- Project Content -->
      <form>
        <div class="row mb-3">
          <div class="col-md-8">
            <label for="projectName" class="form-label">Project Name</label>
            <input
              type="text"
              class="form-control"
              id="projectName"
              value="Smart City Implementation"
            />
          </div>
          <div class="col-md-4">
            <label class="form-label">Progress</label>
            <div class="progress" style="height: 25px; margin-top: 7px">
              <div
                class="progress-bar"
                role="progressbar"
                style="width: 75%"
                aria-valuenow="75"
                aria-valuemin="0"
                aria-valuemax="100"
              >
                75%
              </div>
            </div>
          </div>
        </div>

        <div class="mb-3">
          <label for="projectDescription" class="form-label">Description</label>
          <textarea
            class="form-control"
            id="projectDescription"
            rows="3"
          ></textarea>
        </div>

        <div class="row mb-3">
          <div class="col-md-6">
            <label for="startDate" class="form-label">Start Date</label>
            <input type="date" class="form-control" id="startDate" />
          </div>
          <div class="col-md-6">
            <label for="deadline" class="form-label">Deadline</label>
            <input type="date" class="form-control" id="deadline" />
          </div>
        </div>

        <div class="mb-3">
          <label for="projectLogo" class="form-label">Project Logo</label>
          <input type="file" class="form-control" id="projectLogo" />
        </div>

        <div class="mb-3">
          <label class="form-label">Project Images</label>
          <div class="card p-3 text-center">
            <div class="dropzone-area">
              <i class="bi bi-cloud-arrow-up display-4"></i>
              <p>Drag & drop images here or click to upload</p>
            </div>
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">Upload Files (PDF/PPT)</label>
          <div class="card p-3 text-center">
            <div class="dropzone-area">
              <i class="bi bi-file-earmark-arrow-up display-4"></i>
              <p>Drag & drop PDF or PPT files here or click to upload</p>
            </div>
          </div>
        </div>

        <button type="submit" class="btn btn-primary">Save Changes</button>
      </form>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{% static 'dashboard/js/drag_and_drop_upload.js' %}"></script>
  </body>
</html>
EOF

# Update the project settings to include the app and static files configuration
SETTINGS_FILE="$PROJECT_NAME/settings.py"
cat << 'EOF' >> "$SETTINGS_FILE"

# Add the app to the installed apps
INSTALLED_APPS = [
    # ...
    '$APP_NAME',
    # ...
]

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
EOF

# Update the project URLs to include the app URLs
PROJECT_URLS_FILE="$PROJECT_NAME/urls.py"
cat << 'EOF' >> "$PROJECT_URLS_FILE"
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path('', include('$APP_NAME.urls')),
    # ...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
EOF

echo "Django project and app created successfully!"
