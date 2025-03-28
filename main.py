import torch
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from diffusers import StableDiffusionPipeline
import threading

# Create GUI Window first to avoid Tkinter errors
root = tk.Tk()
root.title("Text-to-Image Generator (Stable Diffusion)")
root.geometry("500x550")
root.resizable(False, False)

# Tkinter BooleanVar to control animation
loading_flag = tk.BooleanVar(value=False)

# Load Stable Diffusion model (with error handling)
try:
    label_status = tk.Label(root, text="Loading model, please wait...", font=("Arial", 12), fg="blue")
    label_status.pack(pady=5)
    root.update()  # Force update to show the loading message

    pipeline = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
    pipeline.to("cuda" if torch.cuda.is_available() else "cpu")  # Use GPU if available
    label_status.config(text="Model loaded successfully!", fg="green")

except Exception as e:
    messagebox.showerror("Error", f"Failed to load the model: {e}")
    root.destroy()
    exit()

saved_image = None  # Variable to store the generated image


# Function to update the loading animation
def animate_loading():
    dots = ["", ".", "..", "..."]
    count = 0
    while loading_flag.get():
        label_status.config(text=f"Generating image{dots[count % 4]}", fg="blue")
        root.update_idletasks()
        count += 1
        root.after(500)  # Update every 500ms


# Function to generate an image from text
def generate_image():
    global saved_image
    prompt = entry.get()

    if not prompt:
        messagebox.showerror("Error", "Please enter a text prompt!")
        return

    label_status.config(text="Generating image...", fg="blue")
    btn_generate.config(state=tk.DISABLED)  # Disable button during generation
    loading_flag.set(True)

    # Start loading animation in a separate thread
    threading.Thread(target=animate_loading, daemon=True).start()

    def run_generation():
        global saved_image
        try:
            image = pipeline(prompt).images[0]  # Generate image
            image.thumbnail((300, 300))  # Resize for display
            img_tk = ImageTk.PhotoImage(image)

            label_image.config(image=img_tk)
            label_image.image = img_tk
            saved_image = image  # Store the generated image

            label_status.config(text="Image generated successfully!", fg="green")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate image: {e}")
            label_status.config(text="Image generation failed.", fg="red")

        finally:
            loading_flag.set(False)
            btn_generate.config(state=tk.NORMAL)  # Re-enable button

    # Run image generation in a separate thread
    threading.Thread(target=run_generation, daemon=True).start()


# Function to save the generated image
def save_image():
    if saved_image:
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            try:
                saved_image.save(file_path)
                messagebox.showinfo("Success", f"Image saved as {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")
    else:
        messagebox.showerror("Error", "No image to save!")


# UI Elements
tk.Label(root, text="Enter a text description:", font=("Arial", 12)).pack(pady=5)
entry = tk.Entry(root, width=50)
entry.pack(pady=5)

btn_generate = tk.Button(root, text="Generate Image", command=generate_image, bg="blue", fg="white")
btn_generate.pack(pady=10)

label_status = tk.Label(root, text="", font=("Arial", 10))
label_status.pack()

label_image = tk.Label(root)
label_image.pack(pady=10)

btn_save = tk.Button(root, text="Save Image", command=save_image, bg="green", fg="white")
btn_save.pack(pady=10)

# Run the GUI
root.mainloop()
