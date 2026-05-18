import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from PIL import Image, ImageTk, ImageEnhance
import cv2
import mediapipe as mp
import numpy as np
import threading
import os
from datetime import datetime

# ========== BACKGROUND REMOVAL & CAMERA ==========
mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

class IDPhotoStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("ID Photo Studio – Perfect ID Photos")
        self.root.geometry("1280x800")
        self.root.configure(bg="#1e2a3a")
        
        # Camera
        self.cap = None
        self.running = True
        self.current_frame = None
        self.photo_image = None
        
        # Background settings
        self.bg_type = "color"  # "color" or "image"
        self.bg_color = (52, 152, 219)  # Sky blue (BGR)
        self.bg_image = None
        self.bg_image_cv = None
        self.custom_bg_path = None
        
        # UI Frames
        self.create_sidebar()
        self.create_camera_area()
        
        # Start camera thread
        self.start_camera()
        self.update_preview()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg="#0f172a", width=280, relief=tk.RIDGE, bd=2)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        sidebar.pack_propagate(False)
        
        # Title
        tk.Label(sidebar, text="🎨 BACKGROUNDS", font=("Segoe UI", 16, "bold"),
                 fg="#ffd966", bg="#0f172a").pack(pady=(20,10))
        
        # Solid color buttons
        colors = [
            ("Pure White", "#FFFFFF", (255,255,255)),
            ("Sky Blue", "#3498db", (52,152,219)),
            ("Light Gray", "#C0C0C0", (192,192,192)),
            ("Deep Green", "#1e3c32", (30,60,50)),
            ("Classic Red", "#e74c3c", (231,76,60)),
            ("Warm Beige", "#f5cba7", (245,203,167))
        ]
        tk.Label(sidebar, text="Solid Colors", font=("Segoe UI", 12, "bold"),
                 fg="white", bg="#0f172a").pack(anchor="w", padx=20, pady=(10,5))
        for name, hex_color, bgr in colors:
            btn = tk.Button(sidebar, text=name, bg=hex_color, fg="black" if name!="Pure White" else "#333",
                            font=("Segoe UI", 10), relief=tk.FLAT, bd=0, padx=10, pady=5,
                            command=lambda c=bgr: self.set_solid_background(c))
            btn.pack(fill=tk.X, padx=20, pady=3)
        
        # Custom color picker
        tk.Label(sidebar, text="Custom Color", font=("Segoe UI", 12, "bold"),
                 fg="white", bg="#0f172a").pack(anchor="w", padx=20, pady=(15,5))
        self.color_preview = tk.Label(sidebar, bg="#3498db", width=5, height=1, relief=tk.RAISED)
        self.color_preview.pack(pady=5)
        tk.Button(sidebar, text="Pick Color", command=self.pick_custom_color,
                  bg="#ffd966", fg="#1e2a3a", font=("Segoe UI", 10, "bold")).pack(pady=5)
        
        # Image background upload
        tk.Label(sidebar, text="Image Background", font=("Segoe UI", 12, "bold"),
                 fg="white", bg="#0f172a").pack(anchor="w", padx=20, pady=(15,5))
        tk.Button(sidebar, text="📁 Upload Image", command=self.upload_background_image,
                  bg="#2c3e66", fg="white", font=("Segoe UI", 10)).pack(pady=5)
        
        # Capture button
        tk.Button(sidebar, text="📸 CAPTURE PHOTO", command=self.capture_photo,
                  bg="#e94560", fg="white", font=("Segoe UI", 14, "bold"),
                  relief=tk.RAISED, bd=3, padx=20, pady=10).pack(pady=(30,20))
        
        # Status label
        self.status_label = tk.Label(sidebar, text="Ready", fg="#bbd4ff", bg="#0f172a",
                                     font=("Segoe UI", 9))
        self.status_label.pack(side=tk.BOTTOM, pady=10)
    
    def create_camera_area(self):
        main_frame = tk.Frame(self.root, bg="#1e2a3a")
        main_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Video label
        self.video_label = tk.Label(main_frame, bg="black", relief=tk.SUNKEN, bd=2)
        self.video_label.pack(expand=True, fill=tk.BOTH)
        
        # Captured preview section
        preview_frame = tk.Frame(main_frame, bg="#1e2a3a")
        preview_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(preview_frame, text="Last Captured Photo:", font=("Segoe UI", 12),
                 fg="white", bg="#1e2a3a").pack()
        self.captured_label = tk.Label(preview_frame, bg="#0f172a", relief=tk.RIDGE,
                                       width=40, height=10)
        self.captured_label.pack(pady=5)
        
        # Download button
        self.download_btn = tk.Button(preview_frame, text="💾 Download as PNG",
                                      command=self.download_captured, state=tk.DISABLED,
                                      bg="#2e7d64", fg="white", font=("Segoe UI", 10, "bold"))
        self.download_btn.pack(pady=5)
    
    # ========== BACKGROUND CONTROL ==========
    def set_solid_background(self, bgr_color):
        self.bg_type = "color"
        self.bg_color = bgr_color  # tuple (B,G,R)
        self.status_label.config(text=f"Background: solid color")
        # Update preview color chip
        hex_color = "#{:02x}{:02x}{:02x}".format(bgr_color[2], bgr_color[1], bgr_color[0])
        self.color_preview.config(bg=hex_color)
    
    def pick_custom_color(self):
        color_code = colorchooser.askcolor(title="Choose background color")
        if color_code:
            rgb = color_code[0]
            bgr = (rgb[2], rgb[1], rgb[0])  # convert to BGR
            self.set_solid_background(bgr)
    
    def upload_background_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if file_path:
            self.custom_bg_path = file_path
            # Load image with OpenCV
            img = cv2.imread(file_path)
            if img is not None:
                self.bg_type = "image"
                self.bg_image_cv = img
                self.status_label.config(text=f"Background: image ({os.path.basename(file_path)})")
            else:
                self.status_label.config(text="Error loading image")
    
    # ========== CAMERA & PROCESSING ==========
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.status_label.config(text="ERROR: Cannot open camera")
            return
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # Start reading thread
        self.thread = threading.Thread(target=self.read_frames, daemon=True)
        self.thread.start()
    
    def read_frames(self):
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Flip horizontally for natural mirror
                frame = cv2.flip(frame, 1)
                self.current_frame = frame
            else:
                break
    
    def process_frame(self, frame):
        if frame is None:
            return None
        # MediaPipe expects RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = selfie_segmentation.process(rgb)
        mask = results.segmentation_mask
        # Convert mask to binary (0 or 1)
        condition = mask > 0.5
        condition = np.stack((condition,)*3, axis=-1)
        
        # Prepare background
        h, w = frame.shape[:2]
        if self.bg_type == "color":
            bg = np.full((h, w, 3), self.bg_color, dtype=np.uint8)
        else:  # image
            if self.bg_image_cv is not None:
                # Resize background to match frame
                bg = cv2.resize(self.bg_image_cv, (w, h))
            else:
                # fallback to black
                bg = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Combine foreground and background using mask
        output = np.where(condition, frame, bg)
        # Enhance slightly for "perfect" look
        output = self.enhance_image(output)
        return output
    
    def enhance_image(self, img):
        # Simple brightness/contrast adjustment
        alpha = 1.05  # contrast
        beta = 5      # brightness
        return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    
    def update_preview(self):
        if self.current_frame is not None:
            processed = self.process_frame(self.current_frame)
            if processed is not None:
                # Convert to RGB for Tkinter
                rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
                # Resize to fit label while maintaining aspect
                label_w = self.video_label.winfo_width()
                label_h = self.video_label.winfo_height()
                if label_w > 10 and label_h > 10:
                    img = img.resize((label_w, label_h), Image.Resampling.LANCZOS)
                self.photo_image = ImageTk.PhotoImage(img)
                self.video_label.config(image=self.photo_image)
                self.video_label.image = self.photo_image
        if self.running:
            self.root.after(30, self.update_preview)
    
    def capture_photo(self):
        if self.current_frame is None:
            self.status_label.config(text="No camera frame yet")
            return
        processed = self.process_frame(self.current_frame)
        if processed is not None:
            # Save to memory for later download
            self.last_captured = processed.copy()
            # Display in preview
            rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
            self.captured_label.config(image=photo)
            self.captured_label.image = photo
            self.download_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Photo captured! Click Download to save.")
        else:
            self.status_label.config(text="Capture failed")
    
    def download_captured(self):
        if hasattr(self, 'last_captured'):
            filename = f"id_photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                initialfile=filename,
                filetypes=[("PNG images", "*.png")]
            )
            if file_path:
                cv2.imwrite(file_path, self.last_captured)
                self.status_label.config(text=f"Saved to {os.path.basename(file_path)}")
    
    def on_close(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = IDPhotoStudio(root)
    root.mainloop()
