import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import *
import os
import pymupdf
import numpy as np
from PIL import Image, ImageTk
from pymupdf.utils import scrub
import cv2

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
    global curPage, image_label, next_image, var, check_page, rot, img, img_orig
    rot = 0
    if curPage >= num:
        return
    image_file = "page-" + str(curPage) + ".png"
    img_orig = Image.open(image_file)
    img = ImageTk.PhotoImage(img_orig)
    image_label = Label(window, image=img)
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
    global curPage, scrub_matrix, tables, rotate, rot
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
        rot = 0
        rotate.forget()

def rotat():
    global image_label, rot, img, img_orig
    rot = (rot + 1) % 4
    rotated_img = img_orig.rotate(-90*rot, expand=True)
    img = ImageTk.PhotoImage(rotated_img)
    image_label.config(image=img)
    image_label.image = img


def pageConfirm():
    global curPage, pages, var, scrub_matrix, tables, rot
    if var.get()==1:
        try:
            while int(tables.get()) <= 0:
                messagebox.showwarning("Invalid Tables", "The amount of tables must be greater than 0")
                return
        except Exception as e:
            messagebox.showwarning("Invalid Entry", "Field can only take integers")
        col_edit = np.where(scrub_matrix[0, :] == curPage)[0]
        scrub_matrix[1, col_edit[0]] = tables.get()
        scrub_matrix[2, col_edit[0]] = rot
        tables.delete(0, tk.END)
        tables.forget()
        rot = 0
        rotate.forget()
    check_page.forget()
    curPage +=1
    image_label.forget()
    next_image.forget()
    imageSelection(pages)


def confirmSelection():
    global pages, scrub_matrix, image_label, next_image, check_page, rotate, tables, rot
    if scrub_matrix[0][-1] == pages -1:
        scrub_matrix[1, -1] = tables.get()
        scrub_matrix[2, -1] = rot

    for num in range(0, pages):
        if num not in scrub_matrix[0]:
            try:
                file_path = "page-" + str(num) + ".png"
                os.remove(file_path)
            except Exception as E:
                messagebox.showwarning("Error Cleaning up Files", f"Error occurred in file deletion: {E}")
        else:
            col_search = np.where(scrub_matrix[0, :] == num)[0]
            rot_val = scrub_matrix[2][col_search]
            if  rot_val > 0:
                file_path_rot = "page-" + str(num) + ".png"
                img = Image.open(file_path_rot)
                rotated_img = img.rotate(-90*rot_val, expand=True)
                rotated_img.save(file_path_rot)
    scrub_matrix = np.delete(scrub_matrix, 2, axis=0)
    image_label.forget()
    next_image.forget()
    check_page.forget()
    rotate.forget()
    tables.forget()
    cropping()

def cropping():
    for page in scrub_matrix[0]:
        page = int(page)
        col_search = np.where(scrub_matrix[0, :] == page)[0]

        table_count = int(scrub_matrix[1][col_search])
        img_path = "page-" + str(page) + ".png"
        for t in range(table_count):
            copy_path = "page-" + str(page) + "-table" + str(t) + ".png"
            img = cv2.imread(img_path)

            x,y,w,h = cv2.selectROI("Select ROI", img, showCrosshair=True, fromCenter=False)
            cropped_image = img[y:y+h, x:x+w]
            #cv2.imshow("Cropped Img", cropped_image)
            cv2.waitKey(0)
            cv2.imwrite(copy_path, cropped_image)
            cv2.destroyAllWindows()
        try:
            os.remove(img_path)
        except Exception as E:
            messagebox.showwarning("Error Cleaning up Files", f"Error occurred in file deletion: {E}")


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