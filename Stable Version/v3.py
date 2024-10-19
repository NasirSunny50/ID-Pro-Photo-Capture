import cv2
import tkinter as tk
from tkinter import Label, Button, filedialog, Frame, messagebox
from PIL import Image, ImageTk
import io
import requests

# Constants for ICAO passport size (35mm x 45mm) at 600 DPI
ICAO_WIDTH_PX = 827
ICAO_HEIGHT_PX = 1063
BOX_WIDTH = 450
BOX_HEIGHT = 350
API_KEY = '7xh4R2m83849TzGPdEhF6Bbc'

# Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class PassportPhotoApp:
    def __init__(self, window):
        self.window = window
        self.window.title("ICAO Passport Photo Capture")
        self.window.geometry("1000x600")
        self.window.configure(bg="#f0f0f0")

        # Title Label
        self.title_label = Label(self.window, text="ICAO Passport Photo Capture", font=("Arial", 20, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=10)

        # Container frame to hold both live feed and preview sections
        self.container_frame = Frame(self.window, bg="#f0f0f0")
        self.container_frame.pack(pady=10, padx=10, expand=True, fill="both")

        # Frame for live camera feed (left side)
        self.left_frame = Frame(self.container_frame, bd=2, relief="groove", bg="white", width=BOX_WIDTH, height=BOX_HEIGHT)
        self.left_frame.grid(row=0, column=0, padx=20, pady=10)
        self.left_frame.grid_propagate(False)

        self.label_camera = Label(self.left_frame, text="Live Camera Feed", font=("Arial", 12), bg="white")
        self.label_camera.pack(pady=10)

        # Frame for captured image preview (right side)
        self.right_frame = Frame(self.container_frame, bd=2, relief="groove", bg="white", width=BOX_WIDTH, height=BOX_HEIGHT)
        self.right_frame.grid(row=0, column=1, padx=20, pady=10)
        self.right_frame.grid_propagate(False)

        self.label_captured = Label(self.right_frame, text="Captured Image Preview", font=("Arial", 12), bg="white")
        self.label_captured.pack(pady=10)

        # Control buttons for left side (below the live feed)
        self.button_frame = Frame(self.left_frame, bg="white")
        self.button_frame.pack(pady=20)

        self.capture_button = Button(self.button_frame, text="Capture Photo", font=("Arial", 12), command=self.capture_photo, bg="#4CAF50", fg="white", width=15, height=1)
        self.capture_button.pack(pady=10)

        # Add Account Limit button to check API balance
        self.account_button = Button(self.button_frame, text="Account Limit", font=("Arial", 12), command=self.check_account_limit, bg="#FF9800", fg="white", width=15, height=1)
        self.account_button.pack(pady=10)

        # Control buttons for right side (below captured image)
        self.remove_bg_button = Button(self.right_frame, text="Remove BG", font=("Arial", 12), command=self.remove_background, state='disabled', bg="#FF5722", fg="white", width=15, height=1)
        self.remove_bg_button.pack(pady=10)

        self.save_button = Button(self.right_frame, text="Save Photo", font=("Arial", 12), command=self.save_photo, state='disabled', bg="#2196F3", fg="white", width=15, height=1)
        self.save_button.pack(pady=10)

        self.retake_button = Button(self.right_frame, text="Retake Photo", font=("Arial", 12), command=self.retake_photo, state='disabled', bg="#f44336", fg="white", width=15, height=1)
        self.retake_button.pack(pady=10)

        self.video_capture = cv2.VideoCapture(0)
        self.display_frame()

        self.photo = None  # Placeholder for the captured photo
        self.face_image = None  # Placeholder for the extracted face

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
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the image
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(150, 150))

            if len(faces) > 0:
                # Take the first detected face
                x, y, w, h = faces[0]
                margin = 50  # Add some margin around the face

                # Ensure margins don't go out of bounds
                x = max(0, x - margin)
                y = max(0, y - margin)
                w = min(frame.shape[1] - x, w + 2 * margin)
                h = min(frame.shape[0] - y, h + 2 * margin)

                # Extract the face region with margin
                face_image = frame[y:y+h, x:x+w]
                self.face_image = Image.fromarray(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))

                # Resize to ICAO passport photo size
                self.face_image = self.face_image.resize((ICAO_WIDTH_PX, ICAO_HEIGHT_PX))

                # Preview extracted face
                self.preview_image(self.face_image)

                # Enable buttons for further actions
                self.remove_bg_button.config(state='normal')
                self.save_button.config(state='normal')
                self.retake_button.config(state='normal')
            else:
                messagebox.showwarning("No Face Detected", "No face detected! Please try again.")
                
    def remove_background(self):
        if self.face_image:
            # Convert the face image to bytes
            img_byte_arr = io.BytesIO()
            self.face_image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()

            # Use the remove.bg API to remove the background
            api_key = 'INSERT_YOUR_API_KEY_HERE'
            response = requests.post(
                'https://api.remove.bg/v1.0/removebg',
                files={'image_file': img_byte_arr.getvalue()},
                headers={'X-Api-Key': API_KEY},
                data={'size': 'auto'}
            )

            if response.status_code == requests.codes.ok:
                result_image = Image.open(io.BytesIO(response.content))
                self.preview_image(result_image)
                self.face_image = result_image  # Update the image
            else:
                messagebox.showerror("Error", f"Error: {response.status_code}, {response.text}")

    def preview_image(self, image):
        # Display the captured image in the preview area (right side)
        image_preview = image.resize((BOX_WIDTH, BOX_HEIGHT))  # Resize for preview
        img_tk = ImageTk.PhotoImage(image=image_preview)
        self.label_captured.imgtk = img_tk
        self.label_captured.configure(image=img_tk)

    def retake_photo(self):
        # Reset captured photo and disable buttons
        self.label_captured.config(image="")
        self.face_image = None
        self.remove_bg_button.config(state='disabled')
        self.save_button.config(state='disabled')
        self.retake_button.config(state='disabled')

    def save_photo(self):
        if self.face_image:
            # Prompt user to save the image
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                self.face_image.save(file_path)

    def check_account_limit(self):
        # Check API account balance and free call limits
        api_key = 'INSERT_YOUR_API_KEY_HERE'
        url = 'https://api.remove.bg/v1.0/account'
        headers = {'X-Api-Key': API_KEY}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            account_info = response.json()
            credits = account_info['data']['attributes']['credits']
            free_calls = account_info['data']['attributes']['api']['free_calls']
            
            balance_msg = (
                f"Total Credits: {credits['total']}\n"
                f"Subscription: {credits['subscription']}\n"
                f"Pay-as-you-go: {credits['payg']}\n"
                f"Free API Calls: {free_calls}"
            )
            messagebox.showinfo("Account Limit", balance_msg)
        elif response.status_code == 403:
            messagebox.showerror("Error", "Authentication failed! Check your API key.")
        elif response.status_code == 429:
            messagebox.showerror("Error", "Rate limit exceeded!")
        else:
            messagebox.showerror("Error", f"An error occurred: {response.status_code}")

    def __del__(self):
        self.video_capture.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = PassportPhotoApp(root)
    root.mainloop()
