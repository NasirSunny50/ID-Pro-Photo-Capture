import cv2
import tkinter as tk
from tkinter import Label, Button, filedialog, Frame, messagebox
from PIL import Image, ImageTk
import io
import requests
import time

# Constants for ICAO passport size (35mm x 45mm) at 600 DPI
ICAO_WIDTH_PX = 827
ICAO_HEIGHT_PX = 1063
BOX_WIDTH = 450
BOX_HEIGHT = 350

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

        # Instruction Label for liveliness detection
        self.instruction_label = Label(self.left_frame, text="", font=("Arial", 10), bg="white")
        self.instruction_label.pack(pady=5)

        # Frame for captured image preview (right side)
        self.right_frame = Frame(self.container_frame, bd=2, relief="groove", bg="white", width=BOX_WIDTH, height=BOX_HEIGHT)
        self.right_frame.grid(row=0, column=1, padx=20, pady=10)
        self.right_frame.grid_propagate(False)

        self.label_captured = Label(self.right_frame, text="Captured Image Preview", font=("Arial", 12), bg="white")
        self.label_captured.pack(pady=10)

        # Control buttons for left side (below the live feed)
        self.button_frame = Frame(self.left_frame, bg="white")
        self.button_frame.pack(pady=20)

        self.capture_button = Button(self.button_frame, text="Capture Photo", font=("Arial", 12), command=self.capture_photo, bg="#4CAF50", fg="white", width=15, height=1, state='disabled')
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
        self.check_liveliness()  # Start the liveliness detection
        self.display_frame()

        self.photo = None  # Placeholder for the captured photo
        self.face_image = None  # Placeholder for the extracted face

    def display_frame(self):
        # Read the frame from the webcam
        ret, frame = self.video_capture.read()
        if ret:
            # Convert the frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the image
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(150, 150))

            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

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

    def check_liveliness(self):
        self.instruction_label.config(text="Please move your head up and down for 5 seconds...")
        self.capture_button.config(state='disabled')
        start_time = time.time()
        vertical_movement_detected = False
        
        while time.time() - start_time < 5:
            ret, frame = self.video_capture.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(150, 150))

                if len(faces) > 0:
                    # Indicate vertical movement detection
                    self.instruction_label.config(text="Great! Now move your head left and right for 5 seconds...")
                    vertical_movement_detected = True
                    break

        if vertical_movement_detected:
            start_time = time.time()  # Reset timer for left-right movement
            while time.time() - start_time < 5:
                ret, frame = self.video_capture.read()
                if ret:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(150, 150))

                    if len(faces) > 0:
                        # Indicate successful liveliness detection
                        self.instruction_label.config(text="Liveliness check complete! You may capture your photo.")
                        self.capture_button.config(state='normal')  # Enable capture button
                        return

        # If no movement detected or time exceeded
        self.instruction_label.config(text="Liveliness check failed! Please try again.")
        self.capture_button.config(state='disabled')

    def capture_photo(self):
        # Capture the current frame
        ret, frame = self.video_capture.read()
        if ret:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the image
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(150, 150))

            if len(faces) == 0:
                messagebox.showerror("Error", "No face detected! Please try again.")
                return

            # Assuming the first detected face is the one to capture
            (x, y, w, h) = faces[0]
            face_img = frame[y:y + h, x:x + w]

            # Resize the face image to ICAO size
            face_img_resized = cv2.resize(face_img, (ICAO_WIDTH_PX, ICAO_HEIGHT_PX))
            self.photo = face_img_resized  # Save the captured photo

            # Show the captured image in the right preview frame
            img_pil = Image.fromarray(cv2.cvtColor(face_img_resized, cv2.COLOR_BGR2RGB))
            img_tk = ImageTk.PhotoImage(image=img_pil)
            self.label_captured.imgtk = img_tk
            self.label_captured.configure(image=img_tk)

            # Enable buttons
            self.remove_bg_button.config(state='normal')
            self.save_button.config(state='normal')
            self.retake_button.config(state='normal')

    def remove_background(self):
        if self.photo is None:
            messagebox.showerror("Error", "No photo to remove background from!")
            return

        # Call remove.bg API to remove background
        api_key = 'INSERT_YOUR_API_KEY_HERE'  # Replace with your actual API key
        url = 'https://api.remove.bg/v1.0/removebg'
        files = {'image_file': cv2.imencode('.png', self.photo)[1].tobytes()}
        headers = {'X-Api-Key': api_key}

        response = requests.post(url, files=files, headers=headers)

        if response.status_code == requests.codes.ok:
            # Show the image with the background removed
            img_no_bg = Image.open(io.BytesIO(response.content))
            img_no_bg_tk = ImageTk.PhotoImage(img_no_bg)
            self.label_captured.imgtk = img_no_bg_tk
            self.label_captured.configure(image=img_no_bg_tk)
        else:
            messagebox.showerror("Error", f"Error: {response.status_code}, {response.text}")

    def save_photo(self):
        if self.photo is None:
            messagebox.showerror("Error", "No photo to save!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            cv2.imwrite(file_path, self.photo)
            messagebox.showinfo("Success", "Photo saved successfully!")

    def retake_photo(self):
        self.photo = None  # Clear the captured photo
        self.label_captured.configure(image='')  # Clear the displayed image
        self.remove_bg_button.config(state='disabled')
        self.save_button.config(state='disabled')
        self.retake_button.config(state='disabled')
        self.check_liveliness()  # Restart liveliness detection

    def check_account_limit(self):
        api_key = 'INSERT_YOUR_API_KEY_HERE'  # Replace with your actual API key
        url = 'https://api.remove.bg/v1.0/account'
        headers = {'X-Api-Key': api_key}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            credits = data['data']['attributes']['credits']
            balance_msg = f"Total Credits: {credits['total']}\nSubscription Credits: {credits['subscription']}\nPay-As-You-Go Credits: {credits['payg']}\nEnterprise Credits: {credits['enterprise']}\nFree API Calls: {data['data']['attributes']['api']['free_calls']}"
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
