from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
import os
from tkinter import simpledialog
from PyPDF2 import PdfReader
from vision_ai import ScreenAnalyzer
from groq_llm import TutorChatBot

root = Tk()
root.title("White Board")
root.geometry("1050x570+150+50")
root.config(bg="#f2f3f5")
root.resizable(False, False)

current_x = 0
current_y = 0
start_x = None
start_y = None
color = "black"
active_tool = None  


def locate_xy(event):
    """Locate the starting point of the drawing."""
    global start_x, start_y, current_x, current_y
    start_x, start_y = event.x, event.y
    current_x, current_y = event.x, event.y


def addline(event):
    """Draw freehand lines when no tool is active."""
    global current_x, current_y
    if active_tool is None:  
        canvas.create_line((current_x, current_y, event.x, event.y), width=int(slider.get()),
                           fill=color, capstyle=ROUND, smooth=True)
        current_x, current_y = event.x, event.y

def insertimage():
    global filename
    global f_img
    filename=filedialog.askopenfilename(initialdir=os.getcwd(),title="select image file",
                                        filetypes=[("Image files", "*.jpg *.jpeg *.png"),("All file","new.txt")])
    f_img=tk.PhotoImage(file=filename)
    my_img=canvas.create_image(180,50,image=f_img)
    root.bind("<B3-Motion>",my_callback)

def my_callback(event):
    global f_img
    f_img=tk.PhotoImage(file=filename)
    my_img=canvas.create_image(event.x,event.y,image=f_img)

def add_shape(event):
    """Draw shapes when a tool (rectangle or oval) is active."""
    global start_x, start_y, active_tool
    if active_tool == "rectangle":
        canvas.create_rectangle(start_x, start_y, event.x, event.y,
                                outline=color, width=int(slider.get()))
    elif active_tool == "oval":
        canvas.create_oval(start_x, start_y, event.x, event.y,
                           outline=color, width=int(slider.get()))
    active_tool = None


def show_color(new_color):
    """Change the current drawing color."""
    global color
    color = new_color


def new_canvas():
    """Clear the canvas."""
    canvas.delete('all')
    display_pallete()


def set_eraser():
    """Activate the eraser by changing the color to white."""
    global color, active_tool
    active_tool = None  
    color = "white"


def set_rectangle_tool():
    """Activate the rectangle drawing tool."""
    global active_tool
    active_tool = "rectangle"
    

def set_oval_tool():
    """Activate the oval drawing tool."""
    global active_tool
    active_tool = "oval"


def display_pallete():
    """Display a color palette for selecting drawing colors."""
    colors_list = ["black", "gray", "brown4", "red", "orange", "yellow", "green", "blue"]
    for i, color_name in enumerate(colors_list):
        id = colors.create_rectangle((10, 10 + i * 30, 30, 30 + i * 30), fill=color_name)
        colors.tag_bind(id, '<Button-1>', lambda x, col=color_name: show_color(col))


def toggle_chatbot():
    """Toggle the chatbot frame visibility."""
    if chatbot_frame.winfo_ismapped():
        chatbot_frame.place_forget()
    else:
        chatbot_frame.place(x=750, y=200, width=300, height=370)

def toggle_chatbotvai():
    """Toggle the chatbot frame visibility."""
    if chatbotv_frame.winfo_ismapped():
        chatbotv_frame.place_forget()
    else:
        chatbotv_frame.place(x=750, y=200, width=300, height=370)

def minimize_chatbot():
    """Minimize the chatbot frame."""
    chatbot_frame.place_forget()

def minimize_chatbotvai():
    """Minimize the chatbot frame."""
    chatbotv_frame.place_forget()

def handle_query():
    """Handle user queries via the chatbot."""
    query = query_entry.get()
    if query:
        bot = TutorChatBot()
        output = bot.respond(query)
        query_output.config(state='normal')
        query_output.delete("1.0", END)
        query_output.insert(END, output.content)
        query_output.config(state='disabled')

def handlevai_query():
    """Handle user queries about the whiteboard visuals"""
    user_input = query_entryv.get()
    if user_input:
        analyzer = ScreenAnalyzer()
        outputvai= analyzer.analyze_screen(user_input)
        queryv_output.config(state='normal')
        queryv_output.delete("1.0", END)
        queryv_output.insert(END, outputvai)
        queryv_output.config(state='disabled')

color_box = PhotoImage(file="icons/color_section.png")
Label(root, image=color_box, bg='#f2f3f5').place(x=10, y=20)

eraser = PhotoImage(file="icons/eraser1.png")
Button(root, image=eraser, bg="#f2f3f5", command=set_eraser).place(x=30, y=400)

import_image = PhotoImage(file="icons/add_image.png")
Button(root, image=import_image, bg="white", command=insertimage).place(x=30, y=440)


colors = Canvas(root, bg="#fff", width=37, height=300, bd=0)
colors.place(x=30, y=60)
display_pallete()

canvas = Canvas(root, width=930, height=500, background="white", cursor="hand2")
canvas.place(x=100, y=10)
canvas.bind('<Button-1>', locate_xy)
canvas.bind('<B1-Motion>', addline)
canvas.bind('<ButtonRelease-1>', add_shape) 
current_value = tk.DoubleVar()


def get_current_value():
    """Get the current slider value."""
    return '{: .2f}'.format(current_value.get())


def slider_changed(event):
    """Update the label when the slider value changes."""
    value_label.configure(text=get_current_value())


slider = ttk.Scale(root, from_=1, to=10, orient="horizontal", command=slider_changed, variable=current_value)
slider.place(x=30, y=530)

value_label = ttk.Label(root, text=get_current_value())
value_label.place(x=27, y=550)

chatbot_icon = PhotoImage(file="icons/chatbot.png")
chatbot_button = Button(root, image=chatbot_icon, command=toggle_chatbot, bg="#f2f3f5", borderwidth=0)
chatbot_button.place(x=1000, y=520)

chatbot_frame = Frame(root, bg="white", bd=2, relief="solid")
Label(chatbot_frame, text="Ask Query:", bg="white", font=("Arial", 10)).pack(anchor=W, padx=5, pady=2)
query_entry = Entry(chatbot_frame, width=30, font=("Arial", 10))
query_entry.pack(padx=5, pady=2)
Button(chatbot_frame, text="Submit", command=handle_query, bg="white", font=("Arial", 10)).pack(padx=5, pady=2)
query_output = Text(chatbot_frame, height=30, width=35, font=("Arial", 10), state='disabled')
query_output.pack(padx=5, pady=5)
minimize_button = Button(chatbot_frame, text="-", command=minimize_chatbot, bg="white", fg="red")
minimize_button.place(x=260, y=0)

document_icon = PhotoImage(file="icons/document_icon.png")
document_button = Button(root, image=document_icon, bg="#f2f3f5", borderwidth=0)
document_button.place(x=950, y=520)


Button(root, text="Vision AI",command=toggle_chatbotvai,font=("Arial", 10), bg="#f2f3f5").place(x=850, y=520)

chatbotv_frame = Frame(root, bg="white", bd=2, relief="solid")
Label(chatbotv_frame, text="Query about whiteboard visual:", bg="white", font=("Arial", 10)).pack(anchor=W, padx=5, pady=2)
query_entryv = Entry(chatbotv_frame, width=30, font=("Arial", 10))
query_entryv.pack(padx=5, pady=2)
Button(chatbotv_frame, text="Submit",command=handlevai_query, bg="white", font=("Arial", 10)).pack(padx=5, pady=2)
queryv_output = Text(chatbotv_frame, height=30, width=35, font=("Arial", 10), state='disabled')
queryv_output.pack(padx=5, pady=5)
minimize_buttonv = Button(chatbotv_frame, command=minimize_chatbotvai,text="-", bg="white", fg="red")
minimize_buttonv.place(x=260, y=0)


def on_canvas_click(event):
    """Prompt the user to input text and place it on the canvas."""
    global active_tool
    if active_tool == "text":
        text = simpledialog.askstring("Input", "Enter text:")
        if text:
            canvas.create_text(event.x, event.y, text=text, fill=color, font=("Arial", int(slider.get()) * 5))
        active_tool = None  


def set_text_tool():
    """Activate the text adding tool."""
    global active_tool
    active_tool = "text"


slides = []
current_slide = 0

def insert_document():
    """Load and display a document (PDF or DOC) on the canvas."""
    global slides, current_slide
    file_path = filedialog.askopenfilename(
        initialdir=os.getcwd(),
        title="Select Document",
        filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    if not file_path:
        return  
    
    slides = []
    current_slide = 0

    if file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        slides = [page.extract_text() for page in reader.pages]
    elif file_path.endswith('.txt'):
        with open(file_path, 'r') as file:
            slides = file.read().split('\n\n')  
    
    if slides:
        display_slide()

def display_slide():
    """Display the current slide on the canvas."""
    global slides, current_slide
    if 0 <= current_slide < len(slides):
        canvas.delete('all')  # Clear canvas
        display_pallete()  # Redraw color palette
        
        slide_text = slides[current_slide]
        canvas.create_text(
            10, 10,
            anchor=NW,
            text=slide_text,
            font=("Arial", 12),
            fill="black",
            width=900  
        )

def next_slide():
    """Go to the next slide."""
    global current_slide
    if current_slide < len(slides) - 1:
        current_slide += 1
        display_slide()

def previous_slide():
    """Go to the previous slide."""
    global current_slide
    if current_slide > 0:
        current_slide -= 1
        display_slide()

document_button.config(command=insert_document)

Button(root, text="Previous", command=previous_slide, font=("Arial", 10), bg="#f2f3f5").place(x=650, y=520)
Button(root, text="Next", command=next_slide, font=("Arial", 10), bg="#f2f3f5").place(x=720, y=520)
Button(root, text="Text", bg="#f2f3f5", command=set_text_tool, font=("Arial", 10), width=10).place(x=370, y=520)


canvas.bind('<Button-1>', lambda event: on_canvas_click(event) if active_tool == "text" else locate_xy(event))
canvas.bind('<ButtonRelease-1>', add_shape)  


Button(root, text="Rectangle", bg="#f2f3f5", command=set_rectangle_tool, font=("Arial", 10), width=10).place(x=150, y=520)
Button(root, text="Oval", bg="#f2f3f5", command=set_oval_tool, font=("Arial", 10), width=10).place(x=260, y=520)
Button(root, text="Clear Screen", bg="#f2f3f5", command=new_canvas, font=("Arial", 10), width=15).place(x=480, y=520)


root.mainloop()
