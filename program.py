import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import *
import os
import pymupdf
import numpy as np
import time
from PIL import Image



def selectFile():
    global curPage, scrub_matrix
    curPage = 0
    filename = filedialog.askopenfilename(title="Select a file to upload", filetypes=[("pdf file", "*.pdf*")])
    selectFile.grid_forget()
    imageCreation(filename)
    scrub_matrix = np.empty((3,0))

def imageCreation(filename):
    global pages
    doc = pymupdf.open(filename)
    num = doc.page_count
    pages = num
    for page in doc:
        pix = page.get_pixmap(dpi=100)
        pix.save("page-%i.png" % page.number)
    imageSelection(num)

def imageSelection( num):
    global curPage, image_label, next_image, var, check_page
    if curPage >= num:
        return
    image_file = "page-" + str(curPage) + ".png"
    img = tk.PhotoImage(file=image_file)
    image_label = tk.Label(window, image=img)
    image_label.image = img
    image_label.pack()
    var = tk.IntVar()
    next_image = tk.Button(window)
    if curPage == num-1:
        next_image = tk.Button(window, text="Confirm Page Selections", command=confirmSelection)
    else:
        next_image = tk.Button(window, text="Next Image", command=pageConfirm)
    next_image.pack(ipadx=60)
    check_page = tk.Checkbutton(window, text="Scrub Page", variable=var, onvalue=1, offvalue=0, command=page_scrub)
    check_page.pack()



def page_scrub():
    global curPage, scrub_matrix, tables
    if var.get() ==1:
        new_data = [curPage, 0, 0]
        tables = tk.Entry(window)
        tables.pack()
        rotate = tk.Button(window, text="Rotate 90 degrees", command=rotat)
        rotate.pack()
        new_col = np.array(new_data).reshape(3,1)
        scrub_matrix = np.hstack((scrub_matrix, new_col))
    else:
        cols_to_remove = np.where(scrub_matrix[0, :] == curPage)[0]
        scrub_matrix = np.delete(scrub_matrix, cols_to_remove, axis=1)
        tables.delete(0, tk.END)
        tables.forget()

def rotat():
    global image_label
    rot_180= image_label.rotate(180)
    rot_180.show()

def pageConfirm():
    global curPage, pages, var, scrub_matrix, tables
    if var.get()==1:
        try:
            while int(tables.get()) < 0:
                messagebox.showwarning("Invalid Tables", "The amount of tables must be greater than 0")
                return
        except Exception as e:
            messagebox.showwarning("Invalid Entry", "Field can only take integers")
        col_edit = np.where(scrub_matrix[0, :] == curPage)[0]
        scrub_matrix[1, col_edit[0]] = tables.get()
    curPage +=1
    image_label.forget()
    next_image.forget()
    tables.delete(0, tk.END)
    tables.forget()
    check_page.forget()
    imageSelection(pages)


def confirmSelection():
    print("Hallo")



if __name__ == "__main__":
    try:
        os.makedirs("tmpImages", mode=0o777, exist_ok=False)
    except Exception as e:
        for file in os.listdir("tmpImages"):
            file_path = os.path.join("tmpImages", file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    os.chdir("tmpImages")
    window = tk.Tk()
    window.title("SO-Scraper")
    window.geometry("1920x1080")
    selectFile = tk.Button(window, text="Upload File for Processing", command=selectFile)
    selectFile.grid(row=1, column=0, ipady=10)
    window.mainloop()