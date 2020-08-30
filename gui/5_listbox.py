from tkinter import *

rt = Tk()
rt.title("재욱이꺼")
rt.geometry("640x480")

listbox = Listbox(rt, selectmode="extended",height=0) #signle / extended #height만큼만 보여줌(0으로 하면 다 보여줌)
listbox.insert(0,"apple")
listbox.insert(1,"딸기")
listbox.insert(2,"바나나")
listbox.insert(END,"수박")
listbox.insert(END,"포도")
listbox.pack()

def btncmd():
    #삭제
    # listbox.delete(END) #맨 뒤에 항목 삭제
    # listbox.delete(0)  # 맨 앞 항목 삭제

    #갯수확인
    # print("리스트에는",listbox.size())

    #항목 확인
    # print("1부터 3까지 항목 : ", listbox.get(0,2))

    #선택된 항목 확인(위치로 반환)
    print("선택된 항목", listbox.curselection())


btn = Button(rt, text="클릭", command=btncmd)
btn.pack()

rt.mainloop()