import cv2
import tkinter as tk
from tkinter import Label, Button, filedialog, Frame
from PIL import Image, ImageTk
from rembg import remove
import io

# Constants for ICAO passport size (35mm x 45mm) at 600 DPI
ICAO_WIDTH_PX = 827
ICAO_HEIGHT_PX = 1063
BOX_WIDTH = 450
BOX_HEIGHT = 350

class PassportPhotoApp:
    def __init__(self, window):
        self.window = window
        self.window.title("ICAO Passport Photo Capture")
        self.window.geometry("1000x600")
        self.window.configure(bg="#f0f0f0")  # Background color

        # Title Label
        self.title_label = Label(self.window, text="ICAO Passport Photo Capture", font=("Arial", 20, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=10)

        # Container frame to hold both live feed and preview sections
        self.container_frame = Frame(self.window, bg="#f0f0f0")
        self.container_frame.pack(pady=10, padx=10, expand=True, fill="both")

        # Frame for live camera feed (left side)
        self.left_frame = Frame(self.container_frame, bd=2, relief="groove", bg="white", width=BOX_WIDTH, height=BOX_HEIGHT)
        self.left_frame.grid(row=0, column=0, padx=20, pady=10)
        self.left_frame.grid_propagate(False)  # Prevent resizing

        self.label_camera = Label(self.left_frame, text="Live Camera Feed", font=("Arial", 12), bg="white")
        self.label_camera.pack(pady=10)

        # Frame for captured image preview (right side)
        self.right_frame = Frame(self.container_frame, bd=2, relief="groove", bg="white", width=BOX_WIDTH, height=BOX_HEIGHT)
        self.right_frame.grid(row=0, column=1, padx=150, pady=210)
        self.right_frame.grid_propagate(True)  # Prevent resizing

        self.label_captured = Label(self.right_frame, text="Captured Image Preview", font=("Arial", 12), bg="white")
        self.label_captured.pack(pady=10)

        # Control buttons for left side (below the live feed)
        self.button_frame = Frame(self.left_frame, bg="white")
        self.button_frame.pack(pady=20)

        self.capture_button = Button(self.button_frame, text="Capture Photo", font=("Arial", 12), command=self.capture_photo, bg="#4CAF50", fg="white", width=15, height=1)  # Smaller button
        self.capture_button.pack(pady=10)

        # Control buttons for right side (below captured image)
        self.remove_bg_button = Button(self.right_frame, text="Remove BG", font=("Arial", 12), command=self.remove_background, state='disabled', bg="#FF5722", fg="white", width=15, height=1)  # Shortened button text
        self.remove_bg_button.pack(pady=10)

        self.save_button = Button(self.right_frame, text="Save Photo", font=("Arial", 12), command=self.save_photo, state='disabled', bg="#2196F3", fg="white", width=15, height=1)  # Smaller button
        self.save_button.pack(pady=10)

        self.retake_button = Button(self.right_frame, text="Retake Photo", font=("Arial", 12), command=self.retake_photo, state='disabled', bg="#f44336", fg="white", width=15, height=1)  # Smaller button
        self.retake_button.pack(pady=10)


        self.video_capture = cv2.VideoCapture(0)
        self.display_frame()

        self.photo = None  # Placeholder for the captured photo

    def display_frame(self):
        # Read the frame from the webcam
        ret, frame = self.video_capture.read()
        if ret:
            # Convert the frame to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image for display
            frame_pil = Image.fromarray(frame_rgb)
            frame_pil = frame_pil.resize((BOX_WIDTH, BOX_HEIGHT))  # Resize for display in the window
            frame_tk = ImageTk.PhotoImage(image=frame_pil)
            self.label_camera.imgtk = frame_tk
            self.label_camera.configure(image=frame_tk)

        # Repeat after 10 ms to keep the video feed running
        self.window.after(10, self.display_frame)

    def capture_photo(self):
        # Capture the current frame
        ret, frame = self.video_capture.read()
        if ret:
            # Convert to RGB for further processing
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image for further processing
            self.photo = Image.fromarray(frame_rgb)
            self.photo = self.photo.resize((ICAO_WIDTH_PX, ICAO_HEIGHT_PX))  # Resize to ICAO size

            # Preview captured image
            self.preview_image(self.photo)

            # Enable buttons for further actions
            self.remove_bg_button.config(state='normal')
            self.save_button.config(state='normal')
            self.retake_button.config(state='normal')

    def remove_background(self):
        if self.photo:
            # Convert the photo to bytes
            img_byte_arr = io.BytesIO()
            self.photo.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()

            # Use rembg to remove the background
            result_bytes = remove(img_bytes)

            # Convert back to PIL Image for preview
            result_image = Image.open(io.BytesIO(result_bytes))
            self.preview_image(result_image)
            self.photo = result_image  # Update the photo to the one with no background

    def preview_image(self, image):
        # Display the captured image in the preview area (right side)
        image_preview = image.resize((350, 250))  # Resize for preview
        img_tk = ImageTk.PhotoImage(image=image_preview)
        self.label_captured.imgtk = img_tk
        self.label_captured.configure(image=img_tk)

    def retake_photo(self):
        # Reset captured photo and disable buttons
        self.label_captured.config(image="")
        self.photo = None
        self.remove_bg_button.config(state='disabled')
        self.save_button.config(state='disabled')
        self.retake_button.config(state='disabled')

    def save_photo(self):
        if self.photo:
            # Prompt user to save the image
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                self.photo.save(file_path)

    def __del__(self):
        # Release the webcam when the app is closed
        self.video_capture.release()

# Initialize Tkinter
root = tk.Tk()
app = PassportPhotoApp(root)
root.mainloop()