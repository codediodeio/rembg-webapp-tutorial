// Get DOM elements
let dropZone = document.getElementById("dropZone");
let fileInput = document.getElementById("fileInput");
let uploadForm = document.getElementById("uploadForm");
let loadingContainer = document.getElementById("loadingContainer");
let previewContainer = document.getElementById("previewContainer");
let originalImage = document.getElementById("originalImage");
let processedImage = document.getElementById("processedImage");
let downloadBtn = document.getElementById("downloadBtn");
let newImageBtn = document.getElementById("newImageBtn");

// Check authentication status on page load
document.addEventListener('DOMContentLoaded', function () {
  checkAuthStatus();
});

async function checkAuthStatus() {
  try {
    const response = await fetch('/auth-status');
    const data = await response.json();

    if (data.auth_required && !data.authenticated) {
      // Clear localStorage auth if server says not authenticated
      localStorage.removeItem('rmbg_auth');
      window.location.href = '/login';
      return;
    }

    // If auth is required and user is authenticated, or no auth required, proceed
    if (data.auth_required && data.authenticated) {
      // Store auth in localStorage if not already stored
      if (!localStorage.getItem('rmbg_auth')) {
        localStorage.setItem('rmbg_auth', 'true');
      }
      addLogoutButton();
    }
  } catch (error) {
    console.error('Auth check failed:', error);
    // On error, redirect to login if localStorage suggests user should be authenticated
    if (localStorage.getItem('rmbg_auth')) {
      localStorage.removeItem('rmbg_auth');
      window.location.href = '/login';
    }
  }
}

function addLogoutButton() {
  // Check if logout button already exists
  if (document.getElementById('logoutBtn')) return;

  // Create logout button
  const logoutBtn = document.createElement('button');
  logoutBtn.id = 'logoutBtn';
  logoutBtn.className = 'logout-btn';
  logoutBtn.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9M16 17L21 12M21 12L16 7M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    Logout
  `;

  logoutBtn.addEventListener('click', function () {
    localStorage.removeItem('rmbg_auth');
    window.location.href = '/logout';
  });

  // Add to the page (top right corner)
  document.body.appendChild(logoutBtn);
}

// Prevent default drag behaviors
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropZone.addEventListener(eventName, preventDefaults, false);
  document.body.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function showLoading() {
  dropZone.classList.add('hidden');
  previewContainer.style.display = 'none';
  loadingContainer.style.display = 'block';
}

function showPreview(data) {
  loadingContainer.style.display = 'none';
  originalImage.src = data.original_image;
  processedImage.src = data.processed_image;
  downloadBtn.href = data.processed_image;

  // Keep original filename and add '_rmbg' before the extension
  const filename = data.filename;
  const lastDotIndex = filename.lastIndexOf('.');
  let newFilename;

  if (lastDotIndex !== -1) {
    // Has extension: "image.jpg" -> "image_rmbg.png"
    const nameWithoutExt = filename.substring(0, lastDotIndex);
    newFilename = nameWithoutExt + "_rmbg.png";
  } else {
    // No extension: "image" -> "image_rmbg.png"
    newFilename = filename + "_rmbg.png";
  }

  downloadBtn.download = newFilename;
  previewContainer.style.display = 'block';
}

function resetToUpload() {
  previewContainer.style.display = 'none';
  loadingContainer.style.display = 'none';
  dropZone.classList.remove('hidden');
  fileInput.value = '';
}

async function processImage(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    showLoading();
    const response = await fetch('/', {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json'
      }
    });

    if (response.status === 401 || response.status === 403) {
      // Authentication failed, redirect to login
      localStorage.removeItem('rmbg_auth');
      window.location.href = '/login';
      return;
    }

    if (response.ok) {
      const data = await response.json();
      showPreview(data);
    } else {
      throw new Error('Processing failed');
    }
  } catch (error) {
    alert('Error processing image: ' + error.message);
    resetToUpload();
  }
}

// Event listeners
dropZone.addEventListener("click", function (e) {
  if (e.target === dropZone || e.target.tagName === 'H1' || e.target.classList.contains('subtitle') || e.target.classList.contains('drag-text') || e.target.closest('.floating')) {
    fileInput.click();
  }
});

fileInput.addEventListener("change", function () {
  if (fileInput.files.length > 0) {
    processImage(fileInput.files[0]);
  }
});

newImageBtn.addEventListener("click", function () {
  resetToUpload();
});

dropZone.addEventListener("dragenter", function (e) {
  this.classList.add("dragover");
});

dropZone.addEventListener("dragover", function (e) {
  this.classList.add("dragover");
});

dropZone.addEventListener("dragleave", function (e) {
  if (!dropZone.contains(e.relatedTarget)) {
    this.classList.remove("dragover");
  }
});

dropZone.addEventListener("drop", function (e) {
  this.classList.remove("dragover");

  let files = e.dataTransfer.files;
  if (files.length > 0) {
    processImage(files[0]);
  }
});