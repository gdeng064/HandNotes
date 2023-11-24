import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter import filedialog
from PIL import ImageGrab
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdfcanvas
import os
import json

# Initialize main window
root = tk.Tk()
root.title("HandNotes")

# Canvas
canvas = tk.Canvas(root, bg="white")
canvas.pack(fill="both", expand=True)

# Global variables
is_drawing = False
is_eraser_on = False
drawing_color = "black"
line_width = 3  # Default to medium thickness

# Function to start drawing
def start_drawing(event):
    global is_drawing, prev_x, prev_y
    is_drawing = True
    prev_x, prev_y = event.x, event.y

# Function for drawing action
def draw(event):
    global is_drawing, prev_x, prev_y
    if is_drawing:
        current_x, current_y = event.x, event.y
        if is_eraser_on:
            canvas.create_rectangle(current_x - 15, current_y - 15, current_x + 15, current_y + 15, fill='white', outline='white')
        else:
            canvas.create_line(prev_x, prev_y, current_x, current_y, fill=drawing_color, width=line_width, capstyle=tk.ROUND, smooth=True)
        prev_x, prev_y = current_x, current_y

# Function to stop drawing
def stop_drawing(event):
    global is_drawing
    is_drawing = False

# Function to change pen color
def change_pen_color():
    global drawing_color
    color = askcolor()[1]
    if color:
        drawing_color = color

# Function to set pen color
def set_pen_color(new_color):
    global drawing_color, is_eraser_on
    drawing_color = new_color
    is_eraser_on = False

# Function to toggle eraser
def toggle_eraser():
    global is_eraser_on
    is_eraser_on = not is_eraser_on

# Function to change line width
def change_line_width(new_width):
    global line_width
    line_width = new_width

# Function to save canvas state
def save_canvas_state():
    canvas_objects = canvas.find_all()
    canvas_data = []
    for item in canvas_objects:
        coords = canvas.coords(item)
        color = canvas.itemcget(item, "fill")
        width = canvas.itemcget(item, "width")
        canvas_data.append({"coords": coords, "color": color, "width": width})
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, "w") as file:
            json.dump(canvas_data, file)

# Function to load canvas state
def load_canvas_state():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        try:
            with open(file_path, "r") as file:
                canvas_data = json.load(file)
            canvas.delete("all")
            for item in canvas_data:
                if len(item["coords"]) == 4:
                    canvas.create_rectangle(*item["coords"], fill=item["color"], outline=item["color"])
                else:
                    canvas.create_line(*item["coords"], fill=item["color"], width=item["width"])
        except FileNotFoundError:
            print("No saved canvas state found.")

# Function to export canvas as PDF
def export_canvas_as_pdf():
    pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if pdf_path:
        try:
            x = root.winfo_rootx() + canvas.winfo_x()
            y = root.winfo_rooty() + canvas.winfo_y()
            x1 = x + canvas.winfo_width()
            y1 = y + canvas.winfo_height()
            canvas_image = ImageGrab.grab().crop((x, y, x1, y1))
            temp_img_path = pdf_path.replace('.pdf', '.png')
            canvas_image.save(temp_img_path)
            c = pdfcanvas.Canvas(pdf_path, pagesize=letter)
            c.drawImage(temp_img_path, 0, 0, letter[0], letter[1])
            c.showPage()
            c.save()
            os.remove(temp_img_path)
            print("Exported to PDF:", pdf_path)
        except Exception as e:
            print("Failed to export PDF:", str(e))

# Add controls to frame
def add_controls_to_frame(frame):
    line_width_var = tk.IntVar()
    line_width_var.set(line_width)
    for width, label in zip([1, 3, 5], ["Thin", "Medium", "Thick"]):
        tk.Radiobutton(frame, text=label, variable=line_width_var, value=width, command=lambda: change_line_width(line_width_var.get())).pack(side='left')
    for color in ['black', 'blue', 'red', 'green']:
        tk.Button(frame, bg=color, width=2, height=1, command=lambda c=color: set_pen_color(c)).pack(side='left')
    tk.Button(frame, text="Pick Color", command=change_pen_color).pack(side='left')
    tk.Button(frame, text="Eraser", command=toggle_eraser).pack(side='left')
    tk.Button(frame, text="Clear Canvas", command=lambda: canvas.delete("all")).pack(side='left')
    tk.Button(frame, text="Save Canvas", command=save_canvas_state).pack(side='left')
    tk.Button(frame, text="Load Canvas", command=load_canvas_state).pack(side='left')
    tk.Button(frame, text="Export as PDF", command=export_canvas_as_pdf).pack(side='left')

# Bind canvas events
canvas.bind("<Button-1>", start_drawing)
canvas.bind("<B1-Motion>", draw)
canvas.bind("<ButtonRelease-1>", stop_drawing)

# Controls frame
controls_frame = tk.Frame(root)
add_controls_to_frame(controls_frame)
controls_frame.pack(side='bottom', fill='x')

root.mainloop()

