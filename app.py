import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import io
import time

# Initialize MediaPipe Selfie Segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

st.set_page_config(page_title="ID Photo Studio", page_icon="📸", layout="wide")

st.title("📸 ID Photo Studio – Perfect ID Photos")
st.markdown("Take a photo with your camera, then replace the background with a solid color or an image.")

# Sidebar controls
st.sidebar.header("Background Settings")

bg_option = st.sidebar.radio("Background type", ["Solid Color", "Upload Image"])

if bg_option == "Solid Color":
    color_hex = st.sidebar.color_picker("Pick a color", "#3498db")
    # Convert hex to BGR
    color_hex = color_hex.lstrip('#')
    bg_color_bgr = tuple(int(color_hex[i:i+2], 16) for i in (4,2,0))  # BGR order for OpenCV
else:
    uploaded_bg = st.sidebar.file_uploader("Upload background image", type=["jpg", "jpeg", "png"])
    if uploaded_bg:
        bg_img = Image.open(uploaded_bg)
        bg_img_cv = cv2.cvtColor(np.array(bg_img), cv2.COLOR_RGB2BGR)
        st.sidebar.image(bg_img, caption="Selected background", use_container_width=True)
    else:
        bg_img_cv = None
        st.sidebar.warning("Please upload an image.")

# Camera input
camera_photo = st.camera_input("Take a photo", key="id_camera")

def enhance_image(img):
    """Simple contrast/brightness adjustment for a fresh look."""
    alpha = 1.05  # contrast
    beta = 5      # brightness
    return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

def replace_background(image_np, bg_type, bg_color=None, bg_image=None):
    h, w = image_np.shape[:2]
    rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    results = selfie_segmentation.process(rgb)
    mask = results.segmentation_mask > 0.5  # boolean mask
    
    if bg_type == "Solid Color":
        bg = np.full((h, w, 3), bg_color, dtype=np.uint8)
    else:  # Uploaded image
        if bg_image is not None:
            bg = cv2.resize(bg_image, (w, h))
        else:
            bg = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Combine using mask
    mask_3ch = np.stack([mask]*3, axis=-1)
    output = np.where(mask_3ch, image_np, bg)
    output = enhance_image(output)
    return output

if camera_photo is not None:
    # Convert Streamlit's uploaded image to OpenCV format
    pil_img = Image.open(camera_photo)
    # Camera input gives RGB, convert to BGR for OpenCV
    image_np = np.array(pil_img)
    image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    
    with st.spinner("Processing background removal..."):
        if bg_option == "Solid Color":
            output = replace_background(image_np, "Solid Color", bg_color=bg_color_bgr)
        else:
            if 'bg_img_cv' in locals() and bg_img_cv is not None:
                output = replace_background(image_np, "Uploaded Image", bg_image=bg_img_cv)
            else:
                st.error("No background image selected. Using solid black fallback.")
                output = replace_background(image_np, "Solid Color", bg_color=(0,0,0))
    
    # Convert back to RGB for display
    output_rgb = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
    result_pil = Image.fromarray(output_rgb)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Photo")
        st.image(camera_photo, use_container_width=True)
    with col2:
        st.subheader("ID Photo with New Background")
        st.image(result_pil, use_container_width=True)
    
    # Download button
    buf = io.BytesIO()
    result_pil.save(buf, format="PNG")
    byte_im = buf.getvalue()
    st.download_button(
        label="💾 Download ID Photo (PNG)",
        data=byte_im,
        file_name=f"id_photo_{int(time.time())}.png",
        mime="image/png"
    )
else:
    st.info("Click the camera above to take a photo, then choose your background style in the sidebar.")
