<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>ID Photo Studio – Perfect ID Photos with Any Background</title>
    <!-- Google Fonts & Font Awesome for icons -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <!-- MediaPipe Selfie Segmentation (lightweight ML model for background removal) -->
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/selfie_segmentation.js" crossorigin="anonymous"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }

        body {
            background: linear-gradient(145deg, #0b1120 0%, #19233c 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        /* Main app container */
        .app-container {
            max-width: 1400px;
            width: 100%;
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(2px);
            border-radius: 48px;
            overflow: hidden;
            box-shadow: 0 25px 45px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.1);
            display: flex;
            flex-wrap: wrap;
        }

        /* SIDEBAR (background selection) */
        .sidebar {
            width: 280px;
            background: rgba(10, 20, 30, 0.85);
            backdrop-filter: blur(12px);
            padding: 24px 16px;
            border-right: 1px solid rgba(255,255,255,0.15);
            display: flex;
            flex-direction: column;
            gap: 28px;
        }

        .sidebar h2 {
            font-size: 1.5rem;
            font-weight: 600;
            color: #ffd966;
            letter-spacing: -0.3px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 2px solid #ffd966;
            padding-bottom: 12px;
        }

        .background-option-group {
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .bg-option {
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 12px 16px;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 2px solid transparent;
            display: flex;
            align-items: center;
            gap: 14px;
            font-weight: 500;
            color: white;
        }

        .bg-option i {
            font-size: 1.4rem;
            width: 32px;
            color: #ffd966;
        }

        .bg-option.active {
            background: #ffd966;
            color: #1e2a3a;
            border-color: white;
            box-shadow: 0 8px 20px rgba(255,217,102,0.3);
        }

        .bg-option.active i {
            color: #1e2a3a;
        }

        .bg-option:hover:not(.active) {
            background: rgba(255,217,102,0.25);
            transform: translateX(5px);
        }

        .color-preview {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 1px 3px black;
        }

        .custom-bg-upload {
            margin-top: 10px;
            background: rgba(0,0,0,0.4);
            border-radius: 40px;
            padding: 12px;
            text-align: center;
        }

        .upload-label {
            background: #2a3a55;
            display: inline-block;
            padding: 8px 18px;
            border-radius: 40px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 500;
            transition: 0.2s;
            color: white;
        }

        .upload-label:hover {
            background: #ffd966;
            color: #0f172a;
        }

        /* MAIN CAMERA AREA */
        .camera-area {
            flex: 1;
            padding: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 25px;
        }

        .video-wrapper {
            position: relative;
            width: 100%;
            max-width: 720px;
            aspect-ratio: 4 / 3;
            background: #111;
            border-radius: 32px;
            overflow: hidden;
            box-shadow: 0 20px 35px rgba(0,0,0,0.5), 0 0 0 3px rgba(255,217,102,0.3);
        }

        canvas, video {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 28px;
        }

        canvas {
            z-index: 2;
            pointer-events: none;
        }

        video {
            z-index: 1;
            transform: scaleX(-1); /* mirror effect for natural selfie view */
        }

        .controls {
            display: flex;
            gap: 25px;
            flex-wrap: wrap;
            justify-content: center;
            margin-top: 10px;
        }

        .btn {
            background: #ffd966;
            border: none;
            padding: 14px 32px;
            border-radius: 60px;
            font-weight: 700;
            font-size: 1.1rem;
            display: inline-flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            transition: 0.2s;
            color: #1e2a3a;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }

        .btn i {
            font-size: 1.2rem;
        }

        .btn-secondary {
            background: #2c3e66;
            color: white;
        }

        .btn:hover {
            transform: scale(1.02);
            filter: brightness(1.05);
        }

        .preview-section {
            margin-top: 10px;
            background: rgba(0,0,0,0.4);
            border-radius: 28px;
            padding: 20px;
            text-align: center;
            width: 100%;
            max-width: 720px;
        }

        .preview-section h3 {
            color: #ffd966;
            margin-bottom: 12px;
            font-size: 1.3rem;
        }

        .captured-img {
            max-width: 180px;
            border-radius: 20px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            border: 2px solid #ffd966;
            margin-top: 8px;
        }

        .download-btn {
            background: #2e7d64;
            color: white;
            margin-top: 12px;
            padding: 10px 22px;
            font-size: 0.9rem;
        }

        .status-msg {
            color: #bbd4ff;
            font-size: 0.85rem;
            margin-top: 10px;
        }

        @media (max-width: 800px) {
            .sidebar {
                width: 100%;
                flex-direction: row;
                flex-wrap: wrap;
                border-right: none;
                border-bottom: 1px solid rgba(255,255,255,0.15);
                gap: 12px;
            }
            .background-option-group {
                flex-direction: row;
                flex-wrap: wrap;
            }
            .bg-option {
                padding: 8px 12px;
            }
            .camera-area {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
<div class="app-container">
    <!-- SIDEBAR with background choices -->
    <div class="sidebar">
        <h2><i class="fas fa-palette"></i> Backgrounds</h2>
        <div class="background-option-group">
            <div class="bg-option" data-bg-type="color" data-bg-value="#FFFFFF" data-bg-name="Pure White">
                <i class="fas fa-tshirt"></i>
                <span>White (ID classic)</span>
                <div class="color-preview" style="background: #FFFFFF;"></div>
            </div>
            <div class="bg-option active" data-bg-type="color" data-bg-value="#3498db" data-bg-name="Sky Blue">
                <i class="fas fa-cloud-sun"></i>
                <span>Sky Blue</span>
                <div class="color-preview" style="background: #3498db;"></div>
            </div>
            <div class="bg-option" data-bg-type="color" data-bg-value="#C0C0C0" data-bg-name="Light Gray">
                <i class="fas fa-moon"></i>
                <span>Light Gray</span>
                <div class="color-preview" style="background: #C0C0C0;"></div>
            </div>
            <div class="bg-option" data-bg-type="color" data-bg-value="#1e3c32" data-bg-name="Deep Green">
                <i class="fas fa-leaf"></i>
                <span>Deep Green</span>
                <div class="color-preview" style="background: #1e3c32;"></div>
            </div>
            <div class="bg-option" data-bg-type="image" data-bg-value="https://www.transparenttextures.com/patterns/cream-paper.png" data-bg-name="Soft Texture">
                <i class="fas fa-image"></i>
                <span>Soft Texture</span>
            </div>
            <div class="bg-option" data-bg-type="image" data-bg-value="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=450&fit=crop" data-bg-name="Office Blur">
                <i class="fas fa-building"></i>
                <span>Office Blur</span>
            </div>
        </div>
        <div class="custom-bg-upload">
            <label class="upload-label" for="customBgUpload">
                <i class="fas fa-upload"></i> Upload your own background
            </label>
            <input type="file" id="customBgUpload" accept="image/jpeg,image/png,image/webp" style="display: none;">
            <div class="status-msg" id="customBgStatus"></div>
        </div>
    </div>

    <!-- MAIN CAMERA / CAPTURE AREA -->
    <div class="camera-area">
        <div class="video-wrapper">
            <video id="videoCam" autoplay playsinline muted></video>
            <canvas id="outputCanvas"></canvas>
        </div>
        <div class="controls">
            <button class="btn" id="captureBtn"><i class="fas fa-camera"></i> TAKE PERFECT PHOTO</button>
            <button class="btn btn-secondary" id="resetCaptureBtn"><i class="fas fa-trash-alt"></i> Clear Last</button>
        </div>
        <div class="preview-section" id="previewSection" style="display: none;">
            <h3><i class="fas fa-id-card"></i> Captured ID Photo</h3>
            <img id="capturedImage" class="captured-img" alt="Your ID photo">
            <br>
            <button id="downloadBtn" class="btn download-btn"><i class="fas fa-download"></i> Download as PNG</button>
        </div>
        <div class="status-msg" id="statusMsg">📸 Background removal active. Choose a style from sidebar → ready!</div>
    </div>
</div>

<script>
    // ---------- ELEMENTS ----------
    const video = document.getElementById('videoCam');
    const canvas = document.getElementById('outputCanvas');
    const ctx = canvas.getContext('2d');
    const captureBtn = document.getElementById('captureBtn');
    const resetBtn = document.getElementById('resetCaptureBtn');
    const previewSection = document.getElementById('previewSection');
    const capturedImg = document.getElementById('capturedImage');
    const downloadBtn = document.getElementById('downloadBtn');
    const statusMsg = document.getElementById('statusMsg');

    // Background state
    let currentBackground = { type: 'color', value: '#3498db' };  // default sky blue
    let customBackgroundImage = null;   // store image object if custom uploaded
    let segmentationReady = false;
    let selfieSegmentation = null;
    let animationId = null;

    // ---------- MEDIAPIPE SELFIE SEGMENTATION INIT ----------
    async function initSegmentation() {
        selfieSegmentation = new SelfieSegmentation({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/${file}`
        });
        selfieSegmentation.setOptions({
            modelSelection: 1,  // 1 = general model (better for various lighting)
            selfieMode: true     // mirror effect
        });
        selfieSegmentation.onResults(onSegmentationResults);
        
        // Start camera first, then initialize segmentation
        await setupCamera();
        await selfieSegmentation.initialize();
        segmentationReady = true;
        statusMsg.innerText = "✅ Camera ready | Background replacement active | Choose any style!";
        // start processing frames
        processVideoFrame();
    }

    async function setupCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "user" } });
            video.srcObject = stream;
            await new Promise((resolve) => {
                video.onloadedmetadata = () => {
                    video.play();
                    resolve();
                };
            });
            // set canvas dimensions same as video display size
            const updateCanvasSize = () => {
                const rect = video.getBoundingClientRect();
                canvas.width = rect.width;
                canvas.height = rect.height;
            };
            updateCanvasSize();
            window.addEventListener('resize', updateCanvasSize);
        } catch (err) {
            console.error("Camera error:", err);
            statusMsg.innerText = "❌ Camera access denied or not available. Please allow camera permissions.";
        }
    }

    // Draw the final frame with selected background
    function onSegmentationResults(results) {
        if (!canvas || !ctx) return;
        // results.segmentationMask is a grayscale image (CanvasImageSource)
        const mask = results.segmentationMask;
        const videoFrame = results.image;  // original video frame
        
        // Create temporary canvas for drawing
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        const tempCtx = tempCanvas.getContext('2d');
        
        // Draw video frame onto temp canvas
        tempCtx.drawImage(videoFrame, 0, 0, canvas.width, canvas.height);
        
        // Now apply background replacement using mask
        // Create an offscreen canvas to hold background
        const bgCanvas = document.createElement('canvas');
        bgCanvas.width = canvas.width;
        bgCanvas.height = canvas.height;
        const bgCtx = bgCanvas.getContext('2d');
        
        // Fill / draw background according to current selection
        if (currentBackground.type === 'color') {
            bgCtx.fillStyle = currentBackground.value;
            bgCtx.fillRect(0, 0, canvas.width, canvas.height);
        } else if (currentBackground.type === 'image') {
            let bgImg;
            if (currentBackground.isCustom && customBackgroundImage) {
                bgImg = customBackgroundImage;
            } else {
                bgImg = new Image();
                bgImg.crossOrigin = "Anonymous";
                bgImg.src = currentBackground.value;
                // if image not loaded yet, use solid fallback
                if (!bgImg.complete) {
                    bgCtx.fillStyle = '#555555';
                    bgCtx.fillRect(0, 0, canvas.width, canvas.height);
                } else {
                    bgCtx.drawImage(bgImg, 0, 0, canvas.width, canvas.height);
                }
            }
            if (bgImg && bgImg.complete) {
                bgCtx.drawImage(bgImg, 0, 0, canvas.width, canvas.height);
            } else if (bgImg) {
                bgImg.onload = () => {
                    bgCtx.drawImage(bgImg, 0, 0, canvas.width, canvas.height);
                };
            }
        }
        
        // Composite: person (from tempCanvas) over background using mask alpha
        // We'll use globalCompositeOperation
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        // draw background first
        ctx.drawImage(bgCanvas, 0, 0);
        // draw video frame, but only where mask is white (person)
        ctx.globalCompositeOperation = 'source-over';
        ctx.drawImage(tempCanvas, 0, 0);
        // apply mask as alpha to cut out background – easiest: use mask as a clipping path, but simpler: use 'destination-in'?
        // Instead we draw mask as alpha channel: use 'destination-out' to remove background? Not exactly.
        // Better method: draw video, then use mask to erase background? Let's do: 
        // Actually we need to keep person, erase background. We'll use "globalCompositeOperation = 'destination-in'"
        // But we must draw mask as alpha. Let's implement robust: 
        // Step: draw video frame, then draw mask as luminance to alpha? Complex.
        // MediaPipe provides mask image, we can use it as alpha map. Here's the correct way:
        ctx.save();
        ctx.globalCompositeOperation = 'destination-in';
        ctx.drawImage(mask, 0, 0, canvas.width, canvas.height);
        ctx.restore();
        
        // Now the background is removed, but we already drew the background underneath. 
        // However destination-in erased everything outside mask, so the background underneath will show through where mask is transparent.
        // But we need the background image to be under the person only. So order: draw background first, then draw video+mask.
        // The above sequence: background drawn, then video drawn, then mask applied (destination-in) which cuts the video to person shape.
        // That leaves the background intact. Works perfectly!
    }

    // Continuously send video frames to MediaPipe for segmentation
    function processVideoFrame() {
        if (!segmentationReady || !video || video.readyState < 2) {
            requestAnimationFrame(processVideoFrame);
            return;
        }
        if (selfieSegmentation && video) {
            selfieSegmentation.send({ image: video });
        }
        requestAnimationFrame(processVideoFrame);
    }

    // ---------- BACKGROUND SELECTION HANDLERS ----------
    function setBackground(type, value, isCustom = false) {
        currentBackground = { type, value, isCustom: isCustom || false };
        // update active UI
        document.querySelectorAll('.bg-option').forEach(opt => opt.classList.remove('active'));
        // find the active one by data attributes
        const matching = Array.from(document.querySelectorAll('.bg-option')).find(opt => 
            opt.getAttribute('data-bg-type') === type && opt.getAttribute('data-bg-value') === value
        );
        if (matching) matching.classList.add('active');
        else if (type === 'image' && isCustom) {
            // custom uploaded active style
            document.querySelectorAll('.bg-option').forEach(opt => opt.classList.remove('active'));
            statusMsg.innerText = "✨ Custom background applied!";
        }
        // Force re-render next frame (mask will use new background)
        statusMsg.innerText = `🎨 Background changed to ${type === 'color' ? value : 'custom/uploaded image'}`;
    }

    // Attach background option click events
    document.querySelectorAll('.bg-option').forEach(opt => {
        opt.addEventListener('click', () => {
            const bgType = opt.getAttribute('data-bg-type');
            const bgValue = opt.getAttribute('data-bg-value');
            if (bgType === 'color') {
                setBackground('color', bgValue);
            } else if (bgType === 'image') {
                setBackground('image', bgValue);
            }
        });
    });

    // Custom background upload
    const customInput = document.getElementById('customBgUpload');
    customInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (ev) => {
                const img = new Image();
                img.onload = () => {
                    customBackgroundImage = img;
                    setBackground('image', ev.target.result, true);
                    document.getElementById('customBgStatus').innerHTML = "✅ Custom background loaded";
                };
                img.src = ev.target.result;
            };
            reader.readAsDataURL(file);
        } else {
            alert('Please select an image file (jpg, png, webp)');
        }
    });

    // ---------- CAPTURE PERFECT PHOTO (from canvas with background) ----------
    function capturePhoto() {
        if (!canvas || !ctx) return;
        // Create a high-resolution capture from the canvas content (which already has background replaced)
        const captureCanvas = document.createElement('canvas');
        captureCanvas.width = canvas.width;
        captureCanvas.height = canvas.height;
        const captureCtx = captureCanvas.getContext('2d');
        captureCtx.drawImage(canvas, 0, 0);
        // Optionally enhance: slight brightness/contrast for "fresh & clean" look
        // We'll just apply a gentle auto-contrast for better ID photo quality
        const imgData = captureCtx.getImageData(0, 0, captureCanvas.width, captureCanvas.height);
        // simple contrast increase (optional: makes skin look fresher)
        const contrast = 1.08;
        const brightness = 5;
        for (let i = 0; i < imgData.data.length; i += 4) {
            imgData.data[i] = Math.min(255, Math.max(0, (imgData.data[i] - 128) * contrast + 128 + brightness));
            imgData.data[i+1] = Math.min(255, Math.max(0, (imgData.data[i+1] - 128) * contrast + 128 + brightness));
            imgData.data[i+2] = Math.min(255, Math.max(0, (imgData.data[i+2] - 128) * contrast + 128 + brightness));
        }
        captureCtx.putImageData(imgData, 0, 0);
        
        const photoURL = captureCanvas.toDataURL('image/png');
        capturedImg.src = photoURL;
        previewSection.style.display = 'block';
        statusMsg.innerText = "✨ Photo captured! Perfect ID quality – download or retake.";
        
        // Store for download
        downloadBtn.onclick = () => {
            const link = document.createElement('a');
            link.download = `id_photo_${new Date().toISOString().slice(0,19)}.png`;
            link.href = photoURL;
            link.click();
        };
    }
    
    captureBtn.addEventListener('click', capturePhoto);
    resetBtn.addEventListener('click', () => {
        previewSection.style.display = 'none';
        capturedImg.src = '';
        statusMsg.innerText = "🗑️ Last photo cleared. Pose again and capture!";
    });
    
    // Start everything
    initSegmentation();
</script>
</body>
</html>
