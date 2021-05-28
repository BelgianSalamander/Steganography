from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import Image, ImageTk
from read import *
from conceal import *

root = Tk()

fp = None

title_frame = Frame(root)
Label(title_frame, text = "Salamander's Steganography", font = ('Helvetica', 32)).pack()
title_frame.grid(column = 0, row = 0)

read_frame = Frame(root)
Label(read_frame, text = "Reveal an image", font = ('Helvetica', 24)).grid(column = 0, row = 0, sticky = W)
img_display = Label(read_frame)
img_display.grid(column = 0, row = 1)

reveal_display = Label(read_frame)
reveal_display.grid(column = 1, row = 1)

revealed_image = None
revealed_download_button = False

def reveal_image():
    global revealed_image, revealed_download_button
    bits = read_bits_from_image(fp)
    img = bits_to_image(bits)
    revealed_image = img
    tk_img = ImageTk.PhotoImage(img.resize((300, 300)))
    reveal_display.config(image = tk_img)
    reveal_display.image = tk_img

    if not revealed_download_button:
        revealed_download_button = True
        download_button.grid(column = 3, row = 2)

reveal = Button(read_frame, text = "Reveal Image", command = reveal_image)
revealed_reveal_button = False

def select_file():
    global revealed_reveal_button, fp
    fp = askopenfilename()
    img = Image.open(fp)
    tk_image = ImageTk.PhotoImage(img.resize((300, 300)))
    img_display.config(image = tk_image)
    img_display.image = tk_image

    if not revealed_reveal_button:
        reveal.grid(column = 1, row = 2)
        revealed_reveal_button = True

def download():
    fp = asksaveasfilename()
    revealed_image.save(fp)

download_button = Button(read_frame, text = "Download Image", command = download)


Button(read_frame, text = "Select Image", command = select_file).grid(column = 0, row = 2)
read_frame.grid(column = 0, row = 1)

root.mainloop()