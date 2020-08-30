from tkinter import *

rt = Tk()
rt.title("재욱이꺼")
rt.geometry("640x480")

label1 = Label(rt, text="Hi")
label1.pack()

photo = PhotoImage(file="check.png")
label2 = Label(rt, image=photo)
label2.pack()

def change():
    label1.config(text="또만나요") #text를 바꿀때 config 쓴다

    global photo2 #가비지컬렉션 되지 않도록 global 변수 설정
    photo2 = PhotoImage(file= "no.png")
    label2.config(image=photo2)

btn = Button(rt, text="click", command=change)
btn.pack()

rt.mainloop()