from tkinter import *
import tkinter.ttk as ttk
import time

rt = Tk()
rt.title("재욱이꺼")
rt.geometry("320x240+700+0")

#pgbar = ttk.Progressbar(rt, maximum=100, mode ="indeterminate")
# pgbar = ttk.Progressbar(rt, maximum=100, mode ="determinate")
# pgbar.start(10)#10ms마다 움직임
# pgbar.pack()
#
#
# def btncmd():
#     pgbar.stop() #작동 중지
#
# btn = Button(rt, text="중지", command=btncmd)
# btn.pack()

p_var2 = DoubleVar()
pbar2 = ttk.Progressbar(rt, maximum=100, length=150, variable=p_var2)
pbar2.pack()

def btncmd2():
    for i in range(1,101):
        time.sleep(0.01)

        p_var2.set(i) #ui update
        pbar2.update()
        print(p_var2.get())

btn = Button(rt, text="시작", command=btncmd2)
btn.pack()

rt.mainloop()