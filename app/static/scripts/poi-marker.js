/**
 * POI Marker Component for A-Frame
 * Creates 3D markers for Points of Interest in VR scenes
 */

AFRAME.registerComponent('poi-marker', {
    schema: {
        poiId: { type: 'string', default: '' },
        type: { type: 'string', default: 'info' }, // info, link, media
        title: { type: 'string', default: 'POI' },
        description: { type: 'string', default: '' },
        imageUrl: { type: 'string', default: '' },
        targetSceneId: { type: 'string', default: '' },
        mediaUrl: { type: 'string', default: '' },
        mediaType: { type: 'string', default: '' }
    },

    init: function () {
        this.marker = null;
        this.isHovered = false;

        this.createMarker();
        this.setupInteractions();
    },

    /**
     * Create 3D marker based on type
     */
    createMarker: function () {
        const data = this.data;
        const el = this.el;

        // Create marker geometry based on type
        let geometry, material;

        if (data.type === 'info') {
            // Blue sphere for info POI
            geometry = new THREE.SphereGeometry(0.15, 16, 16);
            material = new THREE.MeshStandardMaterial({
                color: 0x3b82f6,
                emissive: 0x1e40af,
                emissiveIntensity: 0.5,
                metalness: 0.3,
                roughness: 0.7
            });

        } else if (data.type === 'link') {
            // Green sphere with arrow for link POI
            geometry = new THREE.SphereGeometry(0.15, 16, 16);
            material = new THREE.MeshStandardMaterial({
                color: 0x10b981,
                emissive: 0x059669,
                emissiveIntensity: 0.5,
                metalness: 0.3,
                roughness: 0.7
            });

            // Add arrow indicator
            const arrowGeometry = new THREE.ConeGeometry(0.08, 0.2, 8);
            const arrowMaterial = new THREE.MeshStandardMaterial({
                color: 0x10b981,
                emissive: 0x059669,
                emissiveIntensity: 0.7
            });
            const arrow = new THREE.Mesh(arrowGeometry, arrowMaterial);
            arrow.rotation.x = Math.PI / 2;
            arrow.position.z = -0.25;

            this.arrow = arrow;

        } else if (data.type === 'media') {
            // Purple sphere for media POI
            geometry = new THREE.SphereGeometry(0.15, 16, 16);
            material = new THREE.MeshStandardMaterial({
                color: 0xa855f7,
                emissive: 0x7c3aed,
                emissiveIntensity: 0.5,
                metalness: 0.3,
                roughness: 0.7
            });
        }

        // Create marker mesh
        this.marker = new THREE.Mesh(geometry, material);
        el.setObject3D('marker', this.marker);

        // Add arrow for link type
        if (this.arrow) {
            el.object3D.add(this.arrow);
        }

        // Add pulsing animation
        this.animatePulse();

        // Add glow ring
        this.createGlowRing();
    },

    /**
     * Create glow ring around marker
     */
    createGlowRing: function () {
        const data = this.data;
        const ringGeometry = new THREE.RingGeometry(0.2, 0.25, 32);
        const ringMaterial = new THREE.MeshBasicMaterial({
            color: data.type === 'info' ? 0x3b82f6 :
                   data.type === 'link' ? 0x10b981 : 0xa855f7,
            transparent: true,
            opacity: 0.3,
            side: THREE.DoubleSide
        });

        this.glowRing = new THREE.Mesh(ringGeometry, ringMaterial);
        this.glowRing.rotation.x = -Math.PI / 2;
        this.glowRing.position.y = -0.15;

        this.el.object3D.add(this.glowRing);

        // Animate ring rotation
        this.animateRing();
    },

    /**
     * Animate marker pulsing
     */
    animatePulse: function () {
        const marker = this.marker;
        let scale = 1;
        let growing = true;

        this.pulseInterval = setInterval(() => {
            if (growing) {
                scale += 0.01;
                if (scale >= 1.2) growing = false;
            } else {
                scale -= 0.01;
                if (scale <= 1.0) growing = true;
            }

            marker.scale.set(scale, scale, scale);
        }, 50);
    },

    /**
     * Animate glow ring rotation
     */
    animateRing: function () {
        if (!this.glowRing) return;

        this.el.setAttribute('animation', {
            property: 'object3D.children[1].rotation.z',
            to: '360',
            dur: 3000,
            easing: 'linear',
            loop: true
        });
    },

    /**
     * Setup interaction handlers
     */
    setupInteractions: function () {
        const el = this.el;
        const data = this.data;

        // Mouse enter
        el.addEventListener('mouseenter', () => {
            this.onHoverStart();
        });

        // Mouse leave
        el.addEventListener('mouseleave', () => {
            this.onHoverEnd();
        });

        // Click
        el.addEventListener('click', () => {
            this.onClick();
        });

        // Add cursor property for raycaster
        el.setAttribute('class', 'clickable');
    },

    /**
     * Handle hover start
     */
    onHoverStart: function () {
        this.isHovered = true;

        // Scale up marker
        this.marker.scale.set(1.3, 1.3, 1.3);

        // Increase emissive intensity
        this.marker.material.emissiveIntensity = 1.0;

        // Show tooltip (if responsive-panel component exists)
        this.showTooltip();

        // Change cursor
        document.body.style.cursor = 'pointer';
    },

    /**
     * Handle hover end
     */
    onHoverEnd: function () {
        this.isHovered = false;

        // Reset scale
        this.marker.scale.set(1, 1, 1);

        // Reset emissive
        this.marker.material.emissiveIntensity = 0.5;

        // Hide tooltip
        this.hideTooltip();

        // Reset cursor
        document.body.style.cursor = 'default';
    },

    /**
     * Handle click
     */
    onClick: function () {
        const data = this.data;

        console.log('POI clicked:', data);

        if (data.type === 'info') {
            // Show info panel
            this.showInfoPanel();

        } else if (data.type === 'link') {
            // Navigate to target scene
            this.navigateToScene();

        } else if (data.type === 'media') {
            // Play media
            this.playMedia();
        }
    },

    /**
     * Show info panel
     */
    showInfoPanel: function () {
        const data = this.data;

        // Create responsive panel
        const panel = document.createElement('a-entity');
        panel.setAttribute('responsive-panel', {
            title: data.title,
            description: data.description,
            imageUrl: data.imageUrl
        });

        // Position panel in front of camera
        const camera = document.querySelector('[camera]');
        const cameraPos = camera.object3D.position;
        const cameraRot = camera.object3D.rotation;

        panel.object3D.position.set(
            cameraPos.x,
            cameraPos.y,
            cameraPos.z - 2
        );

        this.el.sceneEl.appendChild(panel);
    },

    /**
     * Navigate to target scene
     */
    navigateToScene: function () {
        const data = this.data;

        if (!data.targetSceneId) {
            console.error('No target scene ID');
            return;
        }

        // Get current space ID from URL or global variable
        const pathParts = window.location.pathname.split('/');
        const spaceIndex = pathParts.indexOf('scene');
        const spaceId = pathParts[spaceIndex + 1];

        // Navigate to target scene
        window.location.href = `/space/scene/${spaceId}/${data.targetSceneId}`;
    },

    /**
     * Play media
     */
    playMedia: function () {
        const data = this.data;

        if (!data.mediaUrl) {
            console.error('No media URL');
            return;
        }

        // Open media in new tab or embedded player
        if (data.mediaType === 'video') {
            // Create video player
            alert('Video player not yet implemented');
        } else if (data.mediaType === 'audio') {
            // Create audio player
            alert('Audio player not yet implemented');
        }
    },

    /**
     * Show tooltip
     */
    showTooltip: function () {
        const data = this.data;

        // Simple text tooltip above marker
        if (!this.tooltip) {
            const tooltipEl = document.createElement('a-entity');
            tooltipEl.setAttribute('text', {
                value: data.title,
                align: 'center',
                width: 2,
                color: '#ffffff',
                shader: 'msdf',
                font: 'https://raw.githubusercontent.com/etiennepinchon/aframe-fonts/master/fonts/roboto/Roboto-Regular.json'
            });
            tooltipEl.setAttribute('position', '0 0.4 0');

            // Add background panel
            const bg = document.createElement('a-plane');
            bg.setAttribute('width', '1.5');
            bg.setAttribute('height', '0.3');
            bg.setAttribute('color', '#000000');
            bg.setAttribute('opacity', '0.7');
            bg.setAttribute('position', '0 0 -0.01');

            tooltipEl.appendChild(bg);
            this.el.appendChild(tooltipEl);
            this.tooltip = tooltipEl;
        }

        this.tooltip.setAttribute('visible', true);
    },

    /**
     * Hide tooltip
     */
    hideTooltip: function () {
        if (this.tooltip) {
            this.tooltip.setAttribute('visible', false);
        }
    },

    /**
     * Component removal
     */
    remove: function () {
        // Clear intervals
        if (this.pulseInterval) {
            clearInterval(this.pulseInterval);
        }
    },

    /**
     * Component tick (runs every frame)
     */
    tick: function (time, deltaTime) {
        // Make marker always face camera
        const camera = this.el.sceneEl.camera;
        if (camera && this.marker) {
            this.marker.lookAt(camera.position);
        }

        // Rotate arrow for link POI
        if (this.arrow) {
            this.arrow.rotation.z = Math.sin(time / 500) * 0.2;
        }
    }
});

console.log('POI Marker component registered');
