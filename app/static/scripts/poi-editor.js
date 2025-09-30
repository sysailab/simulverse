/**
 * POI Editor - Modal and Editor Management
 * Handles POI creation, editing, and modal UI
 */

// Global state
let currentScene = null;
let currentSpace = null;
let selectedImage = null;
let availableScenes = [];

/**
 * Initialize POI Editor
 */
function initPOIEditor(sceneId, spaceId) {
    currentScene = sceneId;
    currentSpace = spaceId;

    // Load available scenes for link POIs
    loadAvailableScenes();

    console.log('POI Editor initialized', { sceneId, spaceId });
}

/**
 * Show POI Modal
 * @param {string} type - POI type: 'info', 'link', or 'media'
 */
function showPOIModal(type = 'info') {
    const modalHTML = `
        <div class="poi-modal-overlay" id="poiModal">
            <div class="poi-modal-container">
                <div class="poi-modal-header">
                    <h2>
                        Add ${type.charAt(0).toUpperCase() + type.slice(1)} POI
                        <span class="poi-type-indicator ${type}">${type}</span>
                    </h2>
                    <button class="poi-modal-close" onclick="closePOIModal()">&times;</button>
                </div>

                <div class="poi-modal-body">
                    <form id="poiForm">
                        <input type="hidden" name="poi_type" value="${type}">

                        <!-- Title -->
                        <div class="poi-form-group">
                            <label>
                                Title <span class="required">*</span>
                            </label>
                            <input type="text" name="title" id="poiTitle" required maxlength="200">
                            <span class="poi-error-message" id="titleError"></span>
                        </div>

                        <!-- Description -->
                        <div class="poi-form-group">
                            <label>Description</label>
                            <textarea name="description" id="poiDescription" maxlength="2000"></textarea>
                            <span class="poi-helper-text">Optional details about this POI</span>
                        </div>

                        <!-- Position -->
                        <div class="poi-form-group">
                            <label>Position <span class="required">*</span></label>
                            <div class="poi-position-grid">
                                <div class="poi-form-group">
                                    <label>X</label>
                                    <input type="number" name="x" id="poiX" step="0.1" value="0" required>
                                </div>
                                <div class="poi-form-group">
                                    <label>Y</label>
                                    <input type="number" name="y" id="poiY" step="0.1" value="1.5" required>
                                </div>
                                <div class="poi-form-group">
                                    <label>Z</label>
                                    <input type="number" name="z" id="poiZ" step="0.1" value="-3" required>
                                </div>
                            </div>
                            <button type="button" class="poi-current-position-btn" onclick="useCurrentPosition()">
                                📍 Use Current Camera Position
                            </button>
                        </div>

                        <!-- Image Upload (Info POI only) -->
                        ${type === 'info' ? `
                        <div class="poi-form-group">
                            <label>Image (Optional)</label>
                            <div class="poi-image-upload" id="imageUpload" onclick="document.getElementById('imageFile').click()">
                                <div class="poi-image-upload-icon">📷</div>
                                <div class="poi-image-upload-text">
                                    <strong>Click to upload</strong> or drag and drop<br>
                                    <small>JPG, PNG up to 10MB</small>
                                </div>
                            </div>
                            <input type="file" id="imageFile" class="poi-file-input" accept="image/jpeg,image/png">
                            <div class="poi-image-preview" id="imagePreview">
                                <img id="previewImg" src="">
                                <div class="poi-image-preview-info" id="imageInfo"></div>
                            </div>
                            <span class="poi-error-message" id="imageError"></span>
                        </div>
                        ` : ''}

                        <!-- Target Scene (Link POI only) -->
                        ${type === 'link' ? `
                        <div class="poi-form-group">
                            <label>Target Scene <span class="required">*</span></label>
                            <select name="target_scene_id" id="targetScene" required>
                                <option value="">Select a scene...</option>
                            </select>
                            <span class="poi-helper-text">Scene to navigate to when clicked</span>
                            <span class="poi-error-message" id="sceneError"></span>
                        </div>
                        ` : ''}

                        <!-- Media URL (Media POI only) -->
                        ${type === 'media' ? `
                        <div class="poi-form-group">
                            <label>Media URL <span class="required">*</span></label>
                            <input type="text" name="media_url" id="mediaUrl" required>
                            <span class="poi-helper-text">URL to video or audio file</span>
                        </div>

                        <div class="poi-form-group">
                            <label>Media Type <span class="required">*</span></label>
                            <select name="media_type" id="mediaType" required>
                                <option value="">Select type...</option>
                                <option value="video">Video</option>
                                <option value="audio">Audio</option>
                            </select>
                        </div>
                        ` : ''}

                        <!-- Visibility -->
                        <div class="poi-form-group">
                            <div class="poi-checkbox-group">
                                <input type="checkbox" name="visible" id="poiVisible" checked>
                                <label for="poiVisible">Visible</label>
                            </div>
                        </div>
                    </form>
                </div>

                <div class="poi-modal-footer">
                    <button type="button" class="poi-btn poi-btn-cancel" onclick="closePOIModal()">
                        Cancel
                    </button>
                    <button type="button" class="poi-btn poi-btn-primary" onclick="submitPOI()" id="submitBtn">
                        Create POI
                    </button>
                </div>
            </div>
        </div>
    `;

    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Show modal with animation
    setTimeout(() => {
        document.getElementById('poiModal').classList.add('active');
    }, 10);

    // Setup modal events
    setupModalEvents(type);

    // Load scenes for link POI
    if (type === 'link') {
        populateSceneDropdown();
    }
}

/**
 * Setup modal event listeners
 */
function setupModalEvents(type) {
    const modal = document.getElementById('poiModal');

    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closePOIModal();
        }
    });

    // Close on ESC key
    document.addEventListener('keydown', handleEscKey);

    // Image upload events (for info POI)
    if (type === 'info') {
        const imageUpload = document.getElementById('imageUpload');
        const imageFile = document.getElementById('imageFile');

        // Drag and drop
        imageUpload.addEventListener('dragover', (e) => {
            e.preventDefault();
            imageUpload.classList.add('dragover');
        });

        imageUpload.addEventListener('dragleave', () => {
            imageUpload.classList.remove('dragover');
        });

        imageUpload.addEventListener('drop', (e) => {
            e.preventDefault();
            imageUpload.classList.remove('dragover');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleImageSelect(files[0]);
            }
        });

        // File input change
        imageFile.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleImageSelect(e.target.files[0]);
            }
        });
    }
}

/**
 * Handle ESC key press
 */
function handleEscKey(e) {
    if (e.key === 'Escape') {
        closePOIModal();
    }
}

/**
 * Close POI Modal
 */
function closePOIModal() {
    const modal = document.getElementById('poiModal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => {
            modal.remove();
            document.removeEventListener('keydown', handleEscKey);
        }, 300);
    }

    // Reset state
    selectedImage = null;
}

/**
 * Handle image selection
 */
function handleImageSelect(file) {
    const imageError = document.getElementById('imageError');

    // Validate file type
    if (!file.type.match('image/jpeg') && !file.type.match('image/png')) {
        imageError.textContent = 'Only JPG and PNG images are allowed';
        imageError.classList.add('active');
        return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
        imageError.textContent = 'Image size must be less than 10MB';
        imageError.classList.add('active');
        return;
    }

    imageError.classList.remove('active');

    // Store file
    selectedImage = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('imageInfo').textContent =
            `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        document.getElementById('imagePreview').classList.add('active');
    };
    reader.readAsDataURL(file);
}

/**
 * Use current camera position for POI
 */
function useCurrentPosition() {
    // Get A-Frame camera
    const camera = document.querySelector('[camera]');
    if (!camera) {
        console.error('Camera not found');
        return;
    }

    // Get camera world position
    const cameraPos = camera.object3D.position;

    // Get camera forward direction (where it's looking)
    const forward = new THREE.Vector3(0, 0, -1);
    forward.applyQuaternion(camera.object3D.quaternion);

    // Place POI 3 units in front of camera
    const poiDistance = 3;
    const poiPos = {
        x: cameraPos.x + forward.x * poiDistance,
        y: cameraPos.y + forward.y * poiDistance,
        z: cameraPos.z + forward.z * poiDistance
    };

    // Update form fields
    document.getElementById('poiX').value = poiPos.x.toFixed(2);
    document.getElementById('poiY').value = poiPos.y.toFixed(2);
    document.getElementById('poiZ').value = poiPos.z.toFixed(2);

    console.log('POI position set to:', poiPos);
}

/**
 * Load available scenes for link POIs
 */
async function loadAvailableScenes() {
    if (!currentSpace) return;

    try {
        const response = await fetch(`/space/scenes/${currentSpace}`);
        const data = await response.json();

        if (data.scenes) {
            availableScenes = data.scenes;
            console.log('Loaded scenes:', availableScenes);
        }
    } catch (error) {
        console.error('Error loading scenes:', error);
    }
}

/**
 * Populate scene dropdown
 */
function populateSceneDropdown() {
    const select = document.getElementById('targetScene');
    if (!select) return;

    // Clear existing options except first
    select.innerHTML = '<option value="">Select a scene...</option>';

    // Add scenes
    availableScenes.forEach(scene => {
        // Don't include current scene
        if (scene.id !== currentScene) {
            const option = document.createElement('option');
            option.value = scene.id;
            option.textContent = scene.name;
            select.appendChild(option);
        }
    });
}

/**
 * Submit POI form
 */
async function submitPOI() {
    const form = document.getElementById('poiForm');
    const submitBtn = document.getElementById('submitBtn');

    // Validate form
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Disable submit button
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="poi-loading"></span> Creating...';

    try {
        // Build form data
        const formData = new FormData(form);

        // Add image if selected
        if (selectedImage) {
            formData.append('image', selectedImage);
        }

        // Add visible checkbox value
        const visible = document.getElementById('poiVisible').checked;
        formData.set('visible', visible);

        // Submit to API
        const response = await fetch(`/space/poi/create/${currentScene}`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            console.log('POI created:', result);
            closePOIModal();

            // Reload scene to show new POI
            location.reload();
        } else {
            throw new Error(result.detail || 'Failed to create POI');
        }

    } catch (error) {
        console.error('Error creating POI:', error);
        alert('Error creating POI: ' + error.message);

        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create POI';
    }
}

// Export functions for global access
window.initPOIEditor = initPOIEditor;
window.showPOIModal = showPOIModal;
window.closePOIModal = closePOIModal;
window.useCurrentPosition = useCurrentPosition;
window.submitPOI = submitPOI;
