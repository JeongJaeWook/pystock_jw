from kiwoom.kiwoom import *

import sys #python system에 쓰는 라이브러리들
from PyQt5.QtWidgets import *

class UI_class: #클래스명 앞글자는 대문자로!
    def __init__(self):
        print("UI 클래스 입니다.")

        self.app = QApplication(sys.argv) #초기화 시키는 용도

        self.kiwoom = Kiwoom()

        self.app.exec_()