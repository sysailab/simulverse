/**
 * POI Editor Component for A-Frame
 * Handles keyboard shortcuts and editor mode for POI management
 */

AFRAME.registerComponent('poi-editor', {
    schema: {
        enabled: { type: 'boolean', default: false }
    },

    init: function () {
        this.editMode = false;
        this.selectedPOI = null;

        if (this.data.enabled) {
            this.setupKeyboardControls();
            this.createEditorUI();
            console.log('POI Editor enabled');
        }
    },

    /**
     * Setup keyboard event listeners
     */
    setupKeyboardControls: function () {
        this.onKeyDown = this.handleKeyPress.bind(this);
        window.addEventListener('keydown', this.onKeyDown);
    },

    /**
     * Handle keyboard shortcuts
     */
    handleKeyPress: function (event) {
        // Ignore if typing in input
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        switch (event.key.toLowerCase()) {
            case 'i':
                // Create Info POI
                event.preventDefault();
                this.addInfoPOI();
                break;

            case 'l':
                // Create Link POI
                event.preventDefault();
                this.addLinkPOI();
                break;

            case 'm':
                // Create Media POI
                event.preventDefault();
                this.addMediaPOI();
                break;

            case 'e':
                // Toggle edit mode
                event.preventDefault();
                this.toggleEditMode();
                break;

            case 'delete':
            case 'backspace':
                // Delete selected POI
                if (this.selectedPOI && this.editMode) {
                    event.preventDefault();
                    this.deletePOI();
                }
                break;

            case 'escape':
                // Cancel edit mode
                event.preventDefault();
                this.deselectPOI();
                break;
        }
    },

    /**
     * Create editor UI indicator
     */
    createEditorUI: function () {
        const ui = document.createElement('div');
        ui.id = 'poi-editor-ui';
        ui.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            z-index: 1000;
            min-width: 200px;
        `;

        ui.innerHTML = `
            <div style="font-size: 14px; font-weight: 600; margin-bottom: 10px;">
                POI Editor
            </div>
            <div style="font-size: 12px; line-height: 1.6;">
                <div><kbd>I</kbd> - Add Info POI</div>
                <div><kbd>L</kbd> - Add Link POI</div>
                <div><kbd>M</kbd> - Add Media POI</div>
                <div><kbd>E</kbd> - Toggle Edit Mode</div>
                <div><kbd>Del</kbd> - Delete Selected</div>
                <div><kbd>Esc</kbd> - Deselect</div>
            </div>
            <div id="editModeIndicator" style="
                margin-top: 10px;
                padding: 5px 10px;
                background: rgba(255,255,255,0.2);
                border-radius: 6px;
                text-align: center;
                font-size: 11px;
                display: none;
            ">
                <span style="color: #10b981;">● </span>EDIT MODE ACTIVE
            </div>
        `;

        document.body.appendChild(ui);
        this.editorUI = ui;
    },

    /**
     * Add Info POI
     */
    addInfoPOI: function () {
        console.log('Adding Info POI');
        if (typeof showPOIModal !== 'undefined') {
            showPOIModal('info');
        } else {
            console.error('showPOIModal function not found');
        }
    },

    /**
     * Add Link POI
     */
    addLinkPOI: function () {
        console.log('Adding Link POI');
        if (typeof showPOIModal !== 'undefined') {
            showPOIModal('link');
        } else {
            console.error('showPOIModal function not found');
        }
    },

    /**
     * Add Media POI
     */
    addMediaPOI: function () {
        console.log('Adding Media POI');
        if (typeof showPOIModal !== 'undefined') {
            showPOIModal('media');
        } else {
            console.error('showPOIModal function not found');
        }
    },

    /**
     * Toggle edit mode
     */
    toggleEditMode: function () {
        this.editMode = !this.editMode;

        const indicator = document.getElementById('editModeIndicator');
        if (indicator) {
            indicator.style.display = this.editMode ? 'block' : 'none';
        }

        if (this.editMode) {
            console.log('Edit mode ENABLED - Click POIs to select them');
            this.enablePOISelection();
        } else {
            console.log('Edit mode DISABLED');
            this.disablePOISelection();
            this.deselectPOI();
        }
    },

    /**
     * Enable POI selection
     */
    enablePOISelection: function () {
        const pois = document.querySelectorAll('[poi-marker]');
        pois.forEach(poi => {
            poi.classList.add('selectable');

            // Add selection handler
            if (!poi._poiClickHandler) {
                poi._poiClickHandler = (e) => {
                    if (this.editMode) {
                        e.stopPropagation();
                        this.selectPOI(poi);
                    }
                };
                poi.addEventListener('click', poi._poiClickHandler);
            }
        });
    },

    /**
     * Disable POI selection
     */
    disablePOISelection: function () {
        const pois = document.querySelectorAll('[poi-marker]');
        pois.forEach(poi => {
            poi.classList.remove('selectable');
        });
    },

    /**
     * Select a POI
     */
    selectPOI: function (poiEl) {
        // Deselect previous
        this.deselectPOI();

        this.selectedPOI = poiEl;
        poiEl.classList.add('selected');

        // Add selection indicator (glow)
        const selectionRing = document.createElement('a-ring');
        selectionRing.setAttribute('radius-inner', '0.3');
        selectionRing.setAttribute('radius-outer', '0.4');
        selectionRing.setAttribute('color', '#fbbf24');
        selectionRing.setAttribute('position', '0 0 0');
        selectionRing.setAttribute('rotation', '-90 0 0');
        selectionRing.setAttribute('animation', {
            property: 'rotation',
            to: '-90 360 0',
            dur: 2000,
            easing: 'linear',
            loop: true
        });
        selectionRing.classList.add('selection-ring');

        poiEl.appendChild(selectionRing);

        console.log('POI selected:', poiEl.getAttribute('poi-marker'));

        // Show edit options
        this.showEditOptions(poiEl);
    },

    /**
     * Deselect current POI
     */
    deselectPOI: function () {
        if (this.selectedPOI) {
            this.selectedPOI.classList.remove('selected');

            // Remove selection ring
            const ring = this.selectedPOI.querySelector('.selection-ring');
            if (ring) {
                ring.parentNode.removeChild(ring);
            }

            this.selectedPOI = null;
            this.hideEditOptions();
        }
    },

    /**
     * Show edit options for selected POI
     */
    showEditOptions: function (poiEl) {
        const poiData = poiEl.getAttribute('poi-marker');

        const options = document.createElement('div');
        options.id = 'poi-edit-options';
        options.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 15px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            display: flex;
            gap: 10px;
            z-index: 1001;
        `;

        options.innerHTML = `
            <button onclick="editSelectedPOI()" style="
                padding: 8px 16px;
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
            ">✏️ Edit</button>
            <button onclick="deleteSelectedPOI()" style="
                padding: 8px 16px;
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
            ">🗑️ Delete</button>
            <button onclick="deselectPOI()" style="
                padding: 8px 16px;
                background: #6b7280;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
            ">✖️ Cancel</button>
        `;

        document.body.appendChild(options);
    },

    /**
     * Hide edit options
     */
    hideEditOptions: function () {
        const options = document.getElementById('poi-edit-options');
        if (options) {
            options.remove();
        }
    },

    /**
     * Delete selected POI
     */
    deletePOI: async function () {
        if (!this.selectedPOI) return;

        const poiData = this.selectedPOI.getAttribute('poi-marker');
        const confirmed = confirm(`Delete POI "${poiData.title}"?`);

        if (!confirmed) return;

        try {
            // Get scene ID from URL or global
            const pathParts = window.location.pathname.split('/');
            const sceneId = pathParts[pathParts.length - 1];

            const response = await fetch(`/space/poi/delete/${sceneId}/${poiData.poiId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                console.log('POI deleted');

                // Remove element
                const poiEl = this.selectedPOI;
                this.deselectPOI();
                poiEl.parentNode.removeChild(poiEl);

                // Optionally reload
                // location.reload();
            } else {
                throw new Error('Failed to delete POI');
            }

        } catch (error) {
            console.error('Error deleting POI:', error);
            alert('Error deleting POI: ' + error.message);
        }
    },

    /**
     * Refresh POIs from server
     */
    async refreshPOIs: function () {
        // Get scene ID
        const pathParts = window.location.pathname.split('/');
        const sceneId = pathParts[pathParts.length - 1];

        try {
            const response = await fetch(`/space/pois/${sceneId}`);
            const data = await response.json();

            if (data.pois) {
                console.log('POIs refreshed:', data.pois.length);
                // Reload scene to update POIs
                location.reload();
            }

        } catch (error) {
            console.error('Error refreshing POIs:', error);
        }
    },

    /**
     * Component removal
     */
    remove: function () {
        if (this.onKeyDown) {
            window.removeEventListener('keydown', this.onKeyDown);
        }

        if (this.editorUI) {
            this.editorUI.remove();
        }

        this.hideEditOptions();
    }
});

// Global functions for button handlers
window.editSelectedPOI = function () {
    const editor = document.querySelector('[poi-editor]');
    if (editor && editor.components['poi-editor'].selectedPOI) {
        // TODO: Open edit modal with POI data
        alert('Edit functionality coming soon');
    }
};

window.deleteSelectedPOI = function () {
    const editor = document.querySelector('[poi-editor]');
    if (editor && editor.components['poi-editor']) {
        editor.components['poi-editor'].deletePOI();
    }
};

window.deselectPOI = function () {
    const editor = document.querySelector('[poi-editor]');
    if (editor && editor.components['poi-editor']) {
        editor.components['poi-editor'].deselectPOI();
    }
};

console.log('POI Editor component registered');
