from tkinter import *

root = Tk()
root.title("jay GUI")
root.geometry("340x240+100+100") #가로*세로 +x좌표 + y좌표
#root.resizable(False, False) # 너비, 높이 값 변경 불가 - 창 크기 변경 X

btn1 = Button(root, text= "버튼1")
btn1.pack() #이걸 호출해줘야 mainloop에 보인다.

btn2 = Button(root, padx=5, pady=10, text= "버튼2222222222222") #여백 정도라 이해 하면 된다.
btn2.pack()

btn3 = Button(root, padx=10, pady=5, text= "버튼3")
btn3.pack()

btn4 = Button(root, width=10,height=3, text="버튼4444444444444444") #고정 크기
btn4.pack()

btn5 = Button(root, fg="red", bg="yellow", text="버튼5")
btn5.pack()

photo = PhotoImage(file = "check.png")
btn6 = Button(root, image=photo)
btn6.pack()

#동작
def btncmd():
    print("버튼 클릭")
btn7 = Button(root, text="동작하는 버튼", command = btncmd)
btn7.pack()

root.mainloop()
