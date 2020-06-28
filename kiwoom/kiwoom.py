from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("Kiwoom() class start.")

        # OCS 방식의 컴포넌트
        # 응용프로그램에서 키움 Open API를 실행할 수 있게 한 것.
        # 즉, 제어가 그낭하다. -> PyQt5에서 제공이 된다.

        ###eventloop 모음
        self.login_event_Loop = None
        self.detail_account_info_event_loop = None
        self.detail_account_info_event_loop2 = None
        ##################

        ###변수 모음
        self.account_num = None
        ##################

        #1일차 + 2일차
        self.get_ocx_instance()
        self.event_slots()
        self.signal_login_commConect()
        self.get_accout_info()

        #3일차
        self.detail_account_info() #예수금

        #4일차
        self.detail_account_mystock() #계좌평가 잔고내역 요청

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")  # 응용 프로그램 제어 가능

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)  # 내가 임의로 만든 slot에다가 결과값을 던져줄것이다.
        self.OnReceiveTrData.connect(self.trdata_slot)  # 실시간 값 받아오기

    def signal_login_commConect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_Loop = QEventLoop()
        self.login_event_Loop.exec_()

    def login_slot(self, errCode):
        print(errors(errCode))
        self.login_event_Loop.exit()

    def get_accout_info(self):
        account_list = self.dynamicCall("GetLogininfo(String)", "ACCNO")
        self.account_num = account_list.split(';')[0]
        print("나의 보유 계좌번호 %s" % self.account_num)  # 8138795411

    def detail_account_info(self):
        print("예수금 요청하는 부분")

        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num);
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000");
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00");
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2");
        self.dynamicCall("CommRqData(String,  String, int,  String) ", "예수금상세현황요청", "opw00001", "0", "2000")

        # 스크린 번호 : 하나의 그룹을 만들어 준다. TR요청 할 때마다 스크린 번호를 기입을 해 줄 건데, 같은 번호끼리 모인다(200개까지가능)
        # 스크린 번호 1개당 100개의 요청 가능

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()  # 동시성 처리 작업 (이벤트 루프안의 큐나 콜백 부분으로 요청 작업이 들어간다.)

    def detail_account_mystock(self, sPrevNext="0"):
        print("계좌평가잔고내역요청")
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num);
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000");
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00");
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2");
        self.dynamicCall("CommRqData(String,  String, int,  String) ", "계좌평가잔고내역요청", "opw00018", sPrevNext, "2000")

        self.detail_account_info_event_loop2 = QEventLoop()
        self.detail_account_info_event_loop2.exec_()

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        '''
        TR요청을 하는 구역(슬롯)
        :param sScrNo: 화면번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청 ID, tr코드
        :param sRecordName: 레코드 -사용안함
        :param sPrevNext: 다음 페이지가 있는지(연속조회 유무를 판단하는 값 0: 연속(추가조회)데이터 없음, 2:연속(추가조회) 데이터 있음)
        :return:
        '''
        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String,String, int, String)", sTrCode, sRQName, 0, "예수금")
            # print("예수금 %s" % type(deposit))
            print("예수금 형 변환 %s" % int(deposit))

            ok_deposit = self.dynamicCall("GetCommData(String,String, int, String)", sTrCode, sRQName, 0, "출금가능금액")
            # print("출금가능금액 %s" % type(ok_deposit))
            print("출금가능금액 형 변환 %s" % int(ok_deposit))
            # Process finished with exit code -1073740791 (0xC0000409) 이렇게 나오면 무조건 오타

            self.detail_account_info_event_loop.exit()  # 이벤트 루프 끊어줘야 함

        if sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(String,String, int, String)", sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)
            print("총매입금액 %s" % total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(String,String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")
            total_profit_loss_rate_result = float(total_profit_loss_rate)
            print("총 수익률(%%) : %s" % total_profit_loss_rate_result)

            self.detail_account_info_event_loop2.exit()  # 이벤트 루프 끊어줘야 함
