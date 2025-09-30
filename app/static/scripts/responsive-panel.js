/**
 * Responsive Panel Component for A-Frame
 * Creates information panels that scale and face the camera
 */

AFRAME.registerComponent('responsive-panel', {
    schema: {
        title: { type: 'string', default: 'Info' },
        description: { type: 'string', default: '' },
        imageUrl: { type: 'string', default: '' },
        width: { type: 'number', default: 2 },
        height: { type: 'number', default: 1.5 }
    },

    init: function () {
        this.panel = null;
        this.camera = null;
        this.initialDistance = 0;
        this.closing = false;

        this.createPanel();
        this.setupCamera();
    },

    /**
     * Create panel with content
     */
    createPanel: function () {
        const data = this.data;
        const el = this.el;

        // Create background panel
        const bg = document.createElement('a-plane');
        bg.setAttribute('width', data.width);
        bg.setAttribute('height', data.height);
        bg.setAttribute('color', '#ffffff');
        bg.setAttribute('opacity', '0.95');
        bg.setAttribute('shader', 'flat');

        // Add shadow/border
        const border = document.createElement('a-plane');
        border.setAttribute('width', data.width + 0.05);
        border.setAttribute('height', data.height + 0.05);
        border.setAttribute('color', '#333333');
        border.setAttribute('opacity', '0.3');
        border.setAttribute('position', '0 0 -0.01');

        bg.appendChild(border);
        el.appendChild(bg);

        // Create content container
        const contentY = data.height / 2 - 0.2;

        // Add title
        if (data.title) {
            const title = document.createElement('a-entity');
            title.setAttribute('text', {
                value: data.title,
                align: 'center',
                width: data.width * 0.9,
                color: '#1f2937',
                wrapCount: 40,
                shader: 'msdf',
                font: 'https://raw.githubusercontent.com/etiennepinchon/aframe-fonts/master/fonts/roboto/Roboto-Bold.json'
            });
            title.setAttribute('position', `0 ${contentY} 0.01`);
            el.appendChild(title);
        }

        // Add description
        if (data.description) {
            const desc = document.createElement('a-entity');
            const descY = data.title ? contentY - 0.3 : contentY;

            desc.setAttribute('text', {
                value: data.description,
                align: 'center',
                width: data.width * 0.85,
                color: '#4b5563',
                wrapCount: 50,
                shader: 'msdf',
                font: 'https://raw.githubusercontent.com/etiennepinchon/aframe-fonts/master/fonts/roboto/Roboto-Regular.json'
            });
            desc.setAttribute('position', `0 ${descY} 0.01`);
            el.appendChild(desc);
        }

        // Add image if provided
        if (data.imageUrl) {
            const imageY = data.description ? -0.2 : 0;
            const imageWidth = data.width * 0.7;
            const imageHeight = imageWidth * 0.6; // 16:10 aspect ratio

            const image = document.createElement('a-image');
            image.setAttribute('src', data.imageUrl);
            image.setAttribute('width', imageWidth);
            image.setAttribute('height', imageHeight);
            image.setAttribute('position', `0 ${imageY} 0.01`);

            el.appendChild(image);
        }

        // Add close button
        this.createCloseButton();

        // Store reference
        this.panel = bg;

        // Animate panel entry
        this.animateEntry();
    },

    /**
     * Create close button
     */
    createCloseButton: function () {
        const data = this.data;
        const buttonSize = 0.2;
        const buttonX = data.width / 2 - buttonSize;
        const buttonY = data.height / 2 - buttonSize;

        // Close button background
        const button = document.createElement('a-circle');
        button.setAttribute('radius', buttonSize);
        button.setAttribute('color', '#ef4444');
        button.setAttribute('position', `${buttonX} ${buttonY} 0.02`);
        button.setAttribute('class', 'clickable');

        // X text
        const xText = document.createElement('a-entity');
        xText.setAttribute('text', {
            value: 'X',
            align: 'center',
            width: 1,
            color: '#ffffff',
            shader: 'msdf',
            font: 'https://raw.githubusercontent.com/etiennepinchon/aframe-fonts/master/fonts/roboto/Roboto-Bold.json'
        });
        xText.setAttribute('position', '0 0 0.01');
        button.appendChild(xText);

        // Click handler
        button.addEventListener('click', () => {
            this.close();
        });

        // Hover effect
        button.addEventListener('mouseenter', () => {
            button.setAttribute('scale', '1.1 1.1 1.1');
            button.setAttribute('color', '#dc2626');
        });

        button.addEventListener('mouseleave', () => {
            button.setAttribute('scale', '1 1 1');
            button.setAttribute('color', '#ef4444');
        });

        this.el.appendChild(button);
        this.closeButton = button;
    },

    /**
     * Setup camera reference and initial distance
     */
    setupCamera: function () {
        this.camera = this.el.sceneEl.camera;

        if (this.camera) {
            const elPos = this.el.object3D.position;
            const camPos = this.camera.position;
            this.initialDistance = elPos.distanceTo(camPos);
        }
    },

    /**
     * Animate panel entry
     */
    animateEntry: function () {
        const el = this.el;

        // Start small and grow
        el.setAttribute('scale', '0.1 0.1 0.1');
        el.setAttribute('animation', {
            property: 'scale',
            to: '1 1 1',
            dur: 300,
            easing: 'easeOutBack'
        });

        // Fade in
        el.setAttribute('animation__fade', {
            property: 'opacity',
            from: 0,
            to: 1,
            dur: 200
        });
    },

    /**
     * Close panel with animation
     */
    close: function () {
        if (this.closing) return;

        this.closing = true;
        const el = this.el;

        // Shrink
        el.setAttribute('animation__close', {
            property: 'scale',
            to: '0.1 0.1 0.1',
            dur: 200,
            easing: 'easeInBack'
        });

        // Fade out
        el.setAttribute('animation__fadeout', {
            property: 'opacity',
            to: 0,
            dur: 200
        });

        // Remove after animation
        setTimeout(() => {
            el.parentNode.removeChild(el);
        }, 250);
    },

    /**
     * Component tick - runs every frame
     */
    tick: function (time, deltaTime) {
        if (!this.camera || this.closing) return;

        const el = this.el;
        const elPos = el.object3D.position;
        const camPos = this.camera.position;

        // Always face camera
        el.object3D.lookAt(camPos);

        // Scale based on distance
        const currentDistance = elPos.distanceTo(camPos);
        const scaleFactor = Math.max(0.5, Math.min(2, currentDistance / this.initialDistance));

        if (!isNaN(scaleFactor)) {
            el.object3D.scale.set(scaleFactor, scaleFactor, scaleFactor);
        }

        // Fade based on distance
        const maxDistance = this.initialDistance * 3;
        const opacity = Math.max(0.3, 1 - (currentDistance - this.initialDistance) / maxDistance);

        if (this.panel && !isNaN(opacity)) {
            this.panel.setAttribute('opacity', Math.max(0.3, Math.min(0.95, opacity)));
        }
    },

    /**
     * Component removal
     */
    remove: function () {
        // Cleanup
        this.panel = null;
        this.camera = null;
        this.closeButton = null;
    }
});

console.log('Responsive Panel component registered');
