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

        ####### event loop를 실행하기 위한 변수모음
        self.login_event_loop = None  # 로그인 요청용 이벤트루프
        self.detail_account_info_event_loop = QEventLoop()  # 예수금 요청용 이벤트루프
        self.calculator_event_loop = QEventLoop()
        #########################################

        ########### 전체 종목 관리
        self.all_stock_dict = {}
        ###########################

        ####### 계좌 관련된 변수
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        self.deposit = 0  # 예수금
        self.use_money = 0  # 실제 투자에 사용할 금액
        self.use_money_percent = 0.5  # 예수금에서 실제 사용할 비율
        self.output_deposit = 0  # 출력가능 금액
        self.total_profit_loss_money = 0  # 총평가손익금액
        self.total_profit_loss_rate = 0.0  # 총수익률(%)
        ########################################

        ######## 종목 정보 가져오기
        self.portfolio_stock_dict = {}
        self.jango_dict = {}
        ########################

        ########### 종목 분석 용
        self.calcul_data = []
        ##########################################

        ####### 요청 스크린 번호
        self.screen_my_info = "2000"  # 계좌 관련한 스크린 번호
        self.screen_calculation_stock = "4000"  # 계산용 스크린 번호
        self.screen_real_stock = "5000"  # 종목별 할당할 스크린 번호
        self.screen_meme_stock = "6000"  # 종목별 할당할 주문용스크린 번호
        self.screen_start_stop_real = "1000"  # 장 시작/종료 실시간 스크린번호
        ########################################

        ######### 초기 셋팅 함수들 바로 실행
        self.get_ocx_instance()  # OCX 방식을 파이썬에 사용할 수 있게 변환해 주는 함수
        self.event_slots()  # 키움과 연결하기 위한 시그널 / 슬롯 모음

        self.signal_login_commConnect()  # 로그인 요청 시그널 포함
        self.get_accout_info()
        self.detail_account_info()  # 예수금 요청 시그널 포함
        self.detail_account_mystock()  # 계좌평가잔고내역 요청 시그널 포함

        # 5일차
        self.not_concluded_account()

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")  # 응용 프로그램 제어 가능 # 레지스트리에 저장된 api 모듈 불러오기

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)  # 내가 임의로 만든 slot에다가 결과값을 던져줄것이다. # 로그인 관련 이벤트
        self.OnReceiveTrData.connect(self.trdata_slot)  # 실시간 값 받아오기 # 트랜잭션 요청 관련 이벤트
        #self.OnReceiveMsg.connect(self.msg_slot)  ##이건뭐야



    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")  # 로그인 요청 시그널
        self.login_event_Loop = QEventLoop() # 이벤트루프 실행
        self.login_event_Loop.exec_()


    def login_slot(self, errCode):
        print(errors(errCode))
        # self.logging.logger.debug(errors(err_code)[1])
        # 로그인 처리가 완료됐으면 이벤트 루프를 종료한다.
        self.login_event_Loop.exit()


    def get_accout_info(self):
        account_list = self.dynamicCall("GetLogininfo(QString)", "ACCNO")
        self.account_num = account_list.split(';')[0]
        print("나의 보유 계좌번호 %s" % self.account_num)  # 8138795411


    # def detail_account_info(self, sPrevNext="0"):
    #     print("예수금 요청하는 부분")
    #
    #     self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
    #     self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
    #     self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
    #     self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
    #     self.dynamicCall("CommRqData(QString,  QString, int,  QString) ", "예수금상세현황요청", "opw00001", sPrevNext, self.screen_my_info)
    #
    #     # 스크린 번호 : 하나의 그룹을 만들어 준다. TR요청 할 때마다 스크린 번호를 기입을 해 줄 건데, 같은 번호끼리 모인다(200개까지가능)
    #     # 스크린 번호 1개당 100개의 요청 가능
    #
    #     self.detail_account_info_event_loop.exec_()  # 동시성 처리 작업 (이벤트 루프안의 큐나 콜백 부분으로 요청 작업이 들어간다.)
    #     print("예수금 요청하는 부분2")

    def detail_account_info(self):
        print("예수금 요청하는 부분")

        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num);
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000");
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00");
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2");
        self.dynamicCall("CommRqData(QString,  QString, int,  QString) ", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)

        # 스크린 번호 : 하나의 그룹을 만들어 준다. TR요청 할 때마다 스크린 번호를 기입을 해 줄 건데, 같은 번호끼리 모인다(200개까지가능)
        # 스크린 번호 1개당 100개의 요청 가능

        #self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()  # 동시성 처리 작업 (이벤트 루프안의 큐나 콜백 부분으로 요청 작업이 들어간다.)

    def detail_account_mystock(self, sPrevNext="0"):
        print("계좌평가 잔고내역 요청 연속조회 %s" % sPrevNext)
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.dynamicCall("CommRqData(QString,  QString, int,  QString) ", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()


    def not_concluded_account(self, sPrevNext="0"):
        print("미체결 내역 조회")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.dynamicCall("CommRqData(QString,  QString, int,  QString) ", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()


    # tr요청 받는 부분 여기서 처리
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
            deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금")
            self.deposit = int(deposit)

            use_money = float(self.deposit) * self.use_money_percent
            self.use_money = int(use_money)
            self.use_money = self.use_money / 4

            output_deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액")
            self.output_deposit = int(output_deposit)

            self.logging.logger.debug("예수금 : %s" % self.output_deposit)

            self.stop_screen_cancel(self.screen_my_info)

            self.detail_account_info_event_loop.exit()

        elif sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액")
            self.total_buy_money = int(total_buy_money)
            total_profit_loss_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액")
            self.total_profit_loss_money = int(total_profit_loss_money)
            total_profit_loss_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)")
            self.total_profit_loss_rate = float(total_profit_loss_rate)

            self.logging.logger.debug(
                "계좌평가잔고내역요청 싱글데이터 : %s - %s - %s" % (total_buy_money, total_profit_loss_money, total_profit_loss_rate))

            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"종목번호")  # 출력 : A039423 // 알파벳 A는 장내주식, J는 ELW종목, Q는 ETN종목
                code = code.strip()[1:]

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")  # 출럭 : 한국기업평가
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")  # 보유수량 : 000000000000010
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")  # 매입가 : 000000000054100
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"수익률(%)")  # 수익률 : -000000001.94
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"현재가")  # 현재가 : 000000003450
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,   "매매가능수량")

                self.logging.logger.debug("종목코드: %s - 종목명: %s - 보유수량: %s - 매입가:%s - 수익률: %s - 현재가: %s" % (code, code_nm, stock_quantity, buy_price, learn_rate, current_price))

                if code in self.account_stock_dict:  # dictionary 에 해당 종목이 있나 확인
                    pass
                else:
                    self.account_stock_dict[code] = {}

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({'매매가능수량': possible_quantity})

            self.logging.logger.debug("sPreNext : %s" % sPrevNext)
            print("계좌에 가지고 있는 종목은 %s " % rows)

            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_info_event_loop.exit()


        elif sRQName == "실시간미체결요청":
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문상태")  # 접수,확인,체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분")  # -매도, +매수, -매도정정, +매수정정
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

                self.not_account_stock_dict[order_no].update({'종목코드': code})
                self.not_account_stock_dict[order_no].update({'종목명': code_nm})
                self.not_account_stock_dict[order_no].update({'주문번호': order_no})
                self.not_account_stock_dict[order_no].update({'주문상태': order_status})
                self.not_account_stock_dict[order_no].update({'주문수량': order_quantity})
                self.not_account_stock_dict[order_no].update({'주문가격': order_price})
                self.not_account_stock_dict[order_no].update({'주문구분': order_gubun})
                self.not_account_stock_dict[order_no].update({'미체결수량': not_quantity})
                self.not_account_stock_dict[order_no].update({'체결량': ok_quantity})

                self.logging.logger.debug("미체결 종목 : %s " % self.not_account_stock_dict[order_no])

            self.detail_account_info_event_loop.exit()



