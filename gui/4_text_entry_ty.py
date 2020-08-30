from tkinter import *

rt = Tk()
rt.title("재욱이꺼")
rt.geometry("640x480")

txt = Text(rt, width=30, height=5)
txt.pack()
txt.insert(END, "글자를 입력하세요")

e = Entry(rt, width=30) #한 줄로 입력 받을 때 사용함
e.pack()
e.insert(0, "한 줄만 입력")

def btncmd():
    #내용 출력
    print(txt.get("1.2", END)) #첨부터 끝까지 가져오기  1: 라인 1 0: 0번째부터
    print(e.get())

    #내용 삭제
    txt.delete("1.0",END)
    e.delete(0,END)

btn = Button(rt, text="클릭", command=btncmd)
btn.pack()

rt.mainloop()