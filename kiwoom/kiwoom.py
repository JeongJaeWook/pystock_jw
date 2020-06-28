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
        self.detail_account_info_event_loop = QEventLoop()
        #self.detail_account_info_event_loop2 = None

        #다시 할당하는게 아니라, 기존꺼를 다시 해야하기 때문에 이렇게 해ㅐ야 한다.
        #중복 경고는 무시해도 댐
        #self.detail_account_info_event_loop2 = QEventLoop()
        ##################

        ###스크린 번호 모음
        self.screen_my_info = "2000"


        ###############

        ###변수 모음
        self.account_num = None
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        ##################

        ###계좌 관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5
        ###########################



        #2일차
        self.get_ocx_instance()
        self.event_slots()
        self.signal_login_commConect()
        self.get_accout_info()

        #3일차
        self.detail_account_info() #예수금

        #4일차
        self.detail_account_mystock() #계좌평가 잔고내역 요청

        #5일차
        self.not_concluded_account()

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
        account_list = self.dynamicCall("GetLogininfo(QString)", "ACCNO")
        self.account_num = account_list.split(';')[0]
        print("나의 보유 계좌번호 %s" % self.account_num)  # 8138795411

    def detail_account_info(self):
        print("예수금 요청하는 부분")

        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num);
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000");
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00");
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2");
        self.dynamicCall("CommRqData(QString,  QString, int,  QString) ", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)

        # 스크린 번호 : 하나의 그룹을 만들어 준다. TR요청 할 때마다 스크린 번호를 기입을 해 줄 건데, 같은 번호끼리 모인다(200개까지가능)
        # 스크린 번호 1개당 100개의 요청 가능

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()  # 동시성 처리 작업 (이벤트 루프안의 큐나 콜백 부분으로 요청 작업이 들어간다.)

    def detail_account_mystock(self, sPrevNext="0"):
        print("계좌평가 잔고내역 요청 연속조회 %s" % sPrevNext)
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num);
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000");
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00");
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2");
        self.dynamicCall("CommRqData(QString,  QString, int,  QString) ", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)


        self.detail_account_info_event_loop.exec_()

    def not_concluded_account(self, sPrevNext="0"):
        print("미체결 내역 조회")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num);
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1");
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0");
        self.dynamicCall("CommRqData(QString,  QString, int,  QString) ", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()


    #tr요청 받는 부분 여기서 처리
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
            deposit = self.dynamicCall("GetCommData(QString,QString, int, QString)", sTrCode, sRQName, 0, "예수금")
            # print("예수금 %s" % type(deposit))
            print("예수금 형 변환 %s" % int(deposit))

            #비중 조절
            self.use_money = int(deposit) * self.use_money_percent #100000 * 0.5 = 50000
            self.use_money = self.use_money / 4 #50000 / 4 = 12500

            ok_deposit = self.dynamicCall("GetCommData(QString,QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액")
            # print("출금가능금액 %s" % type(ok_deposit))
            print("출금가능금액 형 변환 %s" % int(ok_deposit))
            # Process finished with exit code -1073740791 (0xC0000409) 이렇게 나오면 무조건 오타

            self.detail_account_info_event_loop.exit()  # 이벤트 루프 끊어줘야 함

        elif sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(QString,QString, int, QString)", sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)
            print("총매입금액 %s" % total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(QString,QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)")
            total_profit_loss_rate_result = float(total_profit_loss_rate)
            print("총 수익률(%%) : %s" % total_profit_loss_rate_result)

            #보유 종목 코드 갯수 확인
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            ''''
            GetRepeatCnt 는 보유종목 멀티데이터를 가져올 때 사용함
            '''
            cnt = 0 #종목 몇개인지 뽑아보려고

            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})

                #변수 형변환 및 정리(앞에 000 이런거 없애기)
                code = code.strip()[1:]  # 앞에 알파벳을 잘라주는 작업
                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                #사전에 집어넣기
                self.account_stock_dict[code].update({"종목번호":code})
                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt +=1

            print("계좌에 가지고 있는 종목 갯수 %s" % cnt)
            print("계좌에 가지고 있는 종목 %s" % self.account_stock_dict)


            #계좌평가잔고내역 시그널( 다음페이지가 없으면 preVNext 는 0 or "" 값으로 나온다.(잘 기억해야 함)

            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")#첫페이지 0이고 다음페이지 2는 또 요청한다.
            else:
                self.detail_account_info_event_loop.exit()  # 이벤트 루프 끊어줘야 함

        elif sRQName == "실시간미체결요청":
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태") #접수->확인->체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분") #-매도, +매수 - 매도정정, _매수정정
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}


                nasd = self.not_account_stock_dict[order_no]

                nasd.update({"종목코드": code})
                nasd.update({"종목명": code_nm})
                nasd.update({"주문번호": order_no})
                nasd.update({"주문상태": order_status})
                nasd.update({"주문수량": order_quantity})
                nasd.update({"주문가격": order_price})
                nasd.update({"주문구분": order_gubun})
                nasd.update({"미체결수량": not_quantity})
                nasd.update({"체결량": ok_quantity})

                print("미체결 종목: %s" % self.not_account_stock_dict[order_no])

            self.detail_account_info_event_loop.exit()




