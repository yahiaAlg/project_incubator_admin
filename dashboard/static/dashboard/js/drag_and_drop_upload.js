document.addEventListener("DOMContentLoaded", function () {
  const imageUploadArea = document.querySelector(".dropzone-area");
  const fileUploadArea = document.querySelectorAll(".dropzone-area")[1];

  // Store selected files globally
  const selectedFiles = {
    images: [],
    files: [],
  };

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Function to update the visual file list
  function updateFileList(element, inputName) {
    // Remove any existing file list
    const existingList = element.querySelector(".selected-files-list");
    if (existingList) {
      existingList.remove();
    }

    // Create file list if there are files
    if (selectedFiles[inputName].length > 0) {
      const fileList = document.createElement("div");
      fileList.className = "selected-files-list";

      const fileCount = document.createElement("p");
      fileCount.textContent = `${selectedFiles[inputName].length} file(s) selected`;
      fileList.appendChild(fileCount);

      element.appendChild(fileList);
    }
  }

  if (imageUploadArea) {
    initDropArea(
      imageUploadArea,
      ["image/jpeg", "image/png", "image/gif"],
      "images"
    );
  }

  if (fileUploadArea) {
    initDropArea(
      fileUploadArea,
      [
        "application/pdf",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      ],
      "files"
    );
  }

  function initDropArea(element, allowedTypes, inputName) {
    ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
      element.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }

    ["dragenter", "dragover"].forEach((eventName) => {
      element.addEventListener(eventName, () => {
        element.classList.add("drag-highlight");
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      element.addEventListener(eventName, () => {
        element.classList.remove("drag-highlight");
      });
    });

    element.addEventListener("drop", handleDrop);

    element.addEventListener("click", () => {
      const input = document.createElement("input");
      input.type = "file";
      input.multiple = true;

      if (allowedTypes.includes("image/jpeg")) {
        input.accept = "image/*";
      } else if (allowedTypes.includes("application/pdf")) {
        input.accept = ".pdf,.ppt,.pptx";
      }

      input.onchange = (e) => handleFiles(e.target.files, inputName);
      input.click();
    });

    function handleDrop(e) {
      const files = e.dataTransfer.files;
      handleFiles(files, inputName);
    }

    function handleFiles(files, inputName) {
      const fileArray = [...files];
      const validFiles = fileArray.filter((file) => {
        return allowedTypes.some((type) => file.type.match(type));
      });

      if (validFiles.length === 0) {
        showMessage(
          element,
          "No valid files selected. Please upload the correct file type."
        );
        return;
      }

      // Store valid files in the global object
      selectedFiles[inputName] = [...selectedFiles[inputName], ...validFiles];

      showMessage(
        element,
        `Files added for upload: ${validFiles.length}`,
        "success"
      );

      // Update visual feedback to show selected files
      updateFileList(element, inputName);
    }

    function showMessage(element, message, type = "info") {
      const msgElement = document.createElement("div");
      msgElement.className = `upload-message ${type}`;
      msgElement.textContent = message;
      element.appendChild(msgElement);
      setTimeout(() => msgElement.remove(), 5000);
    }
  }

  const style = document.createElement("style");
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
        .selected-files-list {
            margin-top: 10px;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 4px;
        }
    `;
  document.head.appendChild(style);

  function saveProject() {
    const form = document.getElementById("projectForm");
    const formData = new FormData(form);

    // Add the selected files to the FormData object
    selectedFiles.images.forEach((file) => {
      formData.append("images", file);
    });

    selectedFiles.files.forEach((file) => {
      formData.append("files", file);
    });

    fetch("/api/project/save/", {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          alert("Project saved successfully!");
          // Clear selected files after successful upload
          selectedFiles.images = [];
          selectedFiles.files = [];
          // Update visual feedback
          if (imageUploadArea) updateFileList(imageUploadArea, "images");
          if (fileUploadArea) updateFileList(fileUploadArea, "files");
        } else {
          alert("Error saving project.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  const submitBtn = document.getElementById("submitBtn");
  if (submitBtn) {
    submitBtn.addEventListener("click", saveProject);
  }

  // Initialize the date fields with the current date
  const dateFields = document.querySelectorAll("input[type='date']");
  dateFields.forEach((field) => {
    const date = new Date();
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    field.value = `${year}-${month.toString().padStart(2, "0")}-${day
      .toString()
      .padStart(2, "0")}`;
  });
});
