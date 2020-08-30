from tkinter import *
import tkinter.ttk as ttk
rt = Tk()
rt.title("재욱이꺼")
rt.geometry("320x240+700+0")

def create_new_file():
    print("새 파일을 만듭니다.")

menu = Menu(rt)

menu_file = Menu(menu,tearoff=0)
menu_file.add_command(label="New file", command = create_new_file)
menu_file.add_command(label="New Window")
menu_file.add_separator()
menu_file.add_command(label="Open file")
menu_file.add_separator()
menu_file.add_command(label="Save all",state="disable")
menu_file.add_cascade(label="exit",command=rt.quit)
menu.add_cascade(label="file", menu = menu_file)

#m
menu.add_cascade(label="edit")


rt.config(menu=menu)
rt.mainloop()