import streamlit as st
import json
import base64
from PIL import Image
import io
import time

st.set_page_config(page_title="🎨 ID Photo Studio", page_icon="📸", layout="wide")

# ========== COLORFUL CSS ==========
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    }
    h1, h2, h3, .stMarkdown, .stText {
        color: white !important;
    }
    .stButton button {
        background: linear-gradient(90deg, #ff6b6b, #feca57);
        color: white;
        border-radius: 30px;
        font-weight: bold;
        border: none;
        transition: transform 0.2s;
    }
    .stButton button:hover {
        transform: scale(1.02);
        background: linear-gradient(90deg, #ff8e8e, #ffdd87);
    }
    .css-1d391kg {
        background-color: rgba(0,0,0,0.2);
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📸 ID Photo Studio – Perfect ID Photos")
st.markdown("Take a photo, then **instantly replace the background** with a colorful style of your choice.")

# Sidebar with background options
st.sidebar.header("🎨 Background Gallery")

bg_option = st.sidebar.radio(
    "Choose background type",
    ["🌈 Solid Color", "🌅 Gradient", "🖼️ Upload Image"]
)

bg_color = "#3498db"  # default sky blue
if bg_option == "🌈 Solid Color":
    bg_color = st.sidebar.color_picker("Pick a color", "#3498db")
    st.sidebar.markdown(f'<div style="background:{bg_color}; height:50px; border-radius:10px;"></div>', unsafe_allow_html=True)

elif bg_option == "🌅 Gradient":
    gradient_preset = st.sidebar.selectbox(
        "Gradient preset",
        ["Sunset (orange→pink)", "Ocean (blue→green)", "Purple Haze", "Fire (red→yellow)", "Midnight (dark→light)"]
    )
    if gradient_preset == "Sunset (orange→pink)":
        bg_gradient = "linear-gradient(135deg, #ff9a9e, #fad0c4)"
    elif gradient_preset == "Ocean (blue→green)":
        bg_gradient = "linear-gradient(135deg, #00f2fe, #4facfe)"
    elif gradient_preset == "Purple Haze":
        bg_gradient = "linear-gradient(135deg, #a18cd1, #fbc2eb)"
    elif gradient_preset == "Fire (red→yellow)":
        bg_gradient = "linear-gradient(135deg, #ff4b2b, #ff416c)"
    else:
        bg_gradient = "linear-gradient(135deg, #1f4037, #99f2c8)"
    bg_color = bg_gradient  # store as gradient string

else:  # Upload Image
    uploaded_bg = st.sidebar.file_uploader("Upload a background image", type=["jpg", "jpeg", "png"])
    if uploaded_bg:
        bg_image_bytes = uploaded_bg.read()
        bg_color = "image"  # special marker
        st.sidebar.image(uploaded_bg, caption="Your background", use_container_width=True)
    else:
        bg_color = "#2c3e50"  # fallback

# Camera input
camera_photo = st.camera_input("📷 Take a photo", key="id_photo")

# HTML/JS component for background replacement (client-side)
def background_replacement_js(original_image_b64, bg_type, bg_value):
    """
    Returns HTML + JavaScript that replaces background using MediaPipe Selfie Segmentation.
    """
    # For gradients or solid colors, we pass CSS style; for image we pass data URL
    if bg_type == "🌈 Solid Color":
        bg_style = f"background-color: {bg_value};"
    elif bg_type == "🌅 Gradient":
        bg_style = f"background: {bg_value};"
    else:  # image
        bg_style = f"background-image: url('{bg_value}'); background-size: cover; background-position: center;"
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/selfie_segmentation.js"></script>
        <style>
            body {{ margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #222; }}
            .container {{ position: relative; width: 400px; height: 400px; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 35px rgba(0,0,0,0.3); }}
            canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }}
            .controls {{ margin-top: 20px; text-align: center; }}
            button {{ background: #ffd966; border: none; padding: 12px 28px; border-radius: 40px; font-weight: bold; cursor: pointer; font-size: 1rem; }}
            button:hover {{ background: #ffc107; }}
        </style>
    </head>
    <body>
        <div>
            <div class="container">
                <canvas id="outputCanvas" width="400" height="400"></canvas>
            </div>
            <div class="controls">
                <button id="captureBtn">📸 Capture & Download</button>
            </div>
        </div>
        <script>
            const canvas = document.getElementById('outputCanvas');
            const ctx = canvas.getContext('2d');
            let selfieSegmentation = null;
            let originalImage = new Image();
            originalImage.src = "{original_image_b64}";
            let bgStyle = `{bg_style}`;
            
            originalImage.onload = () => {{
                canvas.width = originalImage.width;
                canvas.height = originalImage.height;
                // Initialize MediaPipe
                selfieSegmentation = new SelfieSegmentation({{ locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/${{file}}` }});
                selfieSegmentation.setOptions({{ modelSelection: 1, selfieMode: false }});
                selfieSegmentation.onResults(onResults);
                // Process the image
                selfieSegmentation.send({{ image: originalImage }});
            }};
            
            function onResults(results) {{
                // Draw original image
                ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);
                // Apply mask
                ctx.globalCompositeOperation = 'destination-in';
                ctx.drawImage(results.segmentationMask, 0, 0, canvas.width, canvas.height);
                ctx.globalCompositeOperation = 'source-over';
                // Now draw background underneath (by placing a new background canvas)
                // Simpler: create a temporary canvas with background
                const tempCanvas = document.createElement('canvas');
                tempCanvas.width = canvas.width;
                tempCanvas.height = canvas.height;
                const tempCtx = tempCanvas.getContext('2d');
                // Fill with background style
                if (bgStyle.includes('background-color')) {{
                    const color = bgStyle.match(/background-color:\\s*([^;]+)/)[1];
                    tempCtx.fillStyle = color;
                    tempCtx.fillRect(0, 0, canvas.width, canvas.height);
                }} else if (bgStyle.includes('background-image')) {{
                    const imgUrl = bgStyle.match(/url\\(['"]?([^'"()]+)['"]?\\)/)[1];
                    const bgImg = new Image();
                    bgImg.crossOrigin = "Anonymous";
                    bgImg.src = imgUrl;
                    bgImg.onload = () => {{
                        tempCtx.drawImage(bgImg, 0, 0, canvas.width, canvas.height);
                        // composite: draw person on top
                        tempCtx.drawImage(canvas, 0, 0);
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        ctx.drawImage(tempCanvas, 0, 0);
                    }};
                    return;
                }} else {{
                    // gradient
                    tempCtx.fillStyle = '#ddd';
                    tempCtx.fillRect(0, 0, canvas.width, canvas.height);
                }}
                tempCtx.drawImage(canvas, 0, 0);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(tempCanvas, 0, 0);
            }}
            
            document.getElementById('captureBtn').addEventListener('click', () => {{
                const link = document.createElement('a');
                link.download = 'id_photo.png';
                link.href = canvas.toDataURL();
                link.click();
            }});
        </script>
    </body>
    </html>
    """
    return html_code

if camera_photo is not None:
    # Convert camera image to base64 for the JS component
    pil_img = Image.open(camera_photo)
    # Resize to reasonable size (max 800px)
    pil_img.thumbnail((800, 800))
    buffered = io.BytesIO()
    pil_img.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode()
    data_url = f"data:image/png;base64,{img_b64}"
    
    # Determine background type for JS
    if bg_option == "🌈 Solid Color":
        js_bg_type = "🌈 Solid Color"
        js_bg_value = bg_color
    elif bg_option == "🌅 Gradient":
        js_bg_type = "🌅 Gradient"
        js_bg_value = bg_gradient if 'bg_gradient' in locals() else "linear-gradient(135deg, #667eea, #764ba2)"
    else:  # Upload image
        if uploaded_bg:
            # Convert uploaded background to data URL
            bg_b64 = base64.b64encode(bg_image_bytes).decode()
            js_bg_value = f"data:image/png;base64,{bg_b64}"
            js_bg_type = "image"
        else:
            js_bg_type = "🌈 Solid Color"
            js_bg_value = "#2c3e50"
    
    # Embed the component
    st.markdown("### ✨ Preview & Capture")
    st.components.v1.html(
        background_replacement_js(data_url, js_bg_type, js_bg_value),
        height=550,
        scrolling=False
    )
    st.info("📌 Use the **Capture & Download** button inside the preview to save your ID photo with the new background.")
else:
    st.info("👆 Click the camera above to take a photo first.")

# Footer with colorful message
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #ffd966;'>🎨 Made with vibrant colors | Perfect ID photos in seconds</p>",
    unsafe_allow_html=True
)
