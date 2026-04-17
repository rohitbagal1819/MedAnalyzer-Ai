/**
 * MedAnalyzer AI — Drag & Drop Upload Logic
 */
(function() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const filePreview = document.getElementById('filePreview');
  const uploadBtn = document.getElementById('uploadBtn');
  const uploadForm = document.getElementById('uploadForm');
  const uploadProgress = document.getElementById('uploadProgress');
  const submitArea = document.getElementById('submitArea');

  if (!dropzone || !fileInput) return;

  // Click to browse
  dropzone.addEventListener('click', () => fileInput.click());

  // Drag & drop events
  ['dragenter', 'dragover'].forEach(evt => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(evt => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files;
      handleFile(files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      handleFile(fileInput.files[0]);
    }
  });

  function handleFile(file) {
    const allowedTypes = [
      'application/pdf',
      'image/jpeg', 'image/jpg', 'image/png',
      'image/tiff', 'image/bmp'
    ];

    if (!allowedTypes.includes(file.type)) {
      alert('Invalid file type. Only PDF and image files are allowed.');
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      alert('File is too large. Maximum size is 20MB.');
      return;
    }

    // Show preview
    const fileNameEl = document.getElementById('fileName');
    const fileSizeEl = document.getElementById('fileSize');
    const fileIcon = document.getElementById('fileIcon');

    fileNameEl.textContent = file.name;
    fileSizeEl.textContent = formatFileSize(file.size);
    fileIcon.className = file.type === 'application/pdf' 
      ? 'bi bi-file-pdf' 
      : 'bi bi-file-image';

    filePreview.style.display = 'block';
    dropzone.style.display = 'none';
    uploadBtn.disabled = false;
  }

  // Form submit with progress animation
  if (uploadForm) {
    uploadForm.addEventListener('submit', (e) => {
      // Show progress UI
      uploadProgress.classList.add('active');
      submitArea.style.display = 'none';

      const progressBar = document.getElementById('progressBar');
      const progressLabel = document.getElementById('progressLabel');
      const progressText = document.getElementById('progressText');

      // Animate progress
      let progress = 0;
      const stages = [
        { at: 10, label: 'Uploading report...', text: 'Sending file to server' },
        { at: 30, label: 'Processing with OCR...', text: 'Extracting text from document' },
        { at: 50, label: 'Running NLP analysis...', text: 'Identifying lab values, medications, diseases' },
        { at: 70, label: 'Checking drug interactions...', text: 'Cross-referencing with OpenFDA' },
        { at: 85, label: 'Calculating health score...', text: 'Scoring based on lab normals and anomalies' },
        { at: 95, label: 'Finalizing...', text: 'Saving results to database' }
      ];

      const interval = setInterval(() => {
        progress += Math.random() * 3;
        if (progress > 95) progress = 95;

        progressBar.style.width = progress + '%';

        // Update stage labels
        for (let i = stages.length - 1; i >= 0; i--) {
          if (progress >= stages[i].at) {
            progressLabel.textContent = stages[i].label;
            progressText.textContent = stages[i].text;
            break;
          }
        }
      }, 300);

      // Let form submit naturally (don't prevent default)
      // The progress animation runs while the server processes
    });
  }

  // Clear file
  window.clearFile = function() {
    fileInput.value = '';
    filePreview.style.display = 'none';
    dropzone.style.display = '';
    uploadBtn.disabled = true;
  };

  function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }
})();
