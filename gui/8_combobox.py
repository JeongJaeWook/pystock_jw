from tkinter import *
import tkinter.ttk as ttk
rt = Tk()
rt.title("재욱이꺼")
rt.geometry("320x240+700+0")

values = [str(i) + "일" for i in range(1,32)]
combobox = ttk.Combobox(rt, height=5, values=values)
combobox.pack()
combobox.set("카드 결제일") # 최초 목록 제목 설정

combobox2 = ttk.Combobox(rt, height=0, values=values, state = "readonly")
combobox2.current(0)
combobox2.pack()

def btncmd():
    print(combobox.get())
    print(combobox2.get())

btn = Button(rt, text="클릭", command=btncmd)
btn.pack()

rt.mainloop()