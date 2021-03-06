import os
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from pystock.config.errorCode import *
from PyQt5.QtTest import *


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("Kiwoom() class start.")

        # OCS 방식의 컴포넌트
        # 응용프로그램에서 키움 Open API를 실행할 수 있게 한 것.
        # 즉, 제어가 그낭하다. -> PyQt5에서 제공이 된다.

        ###eventloop 모음
        self.login_event_Loop = QEventLoop()
        self.detail_account_info_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()

        ###스크린 번호 모음
        self.screen_my_info = "2000"
        self.screen_calculation_stock = "4000"
        self.screen_real_stock = "5000" #종목별로 할당할 스크린 번호
        self.screen_meme_stock = "6000" #종목별 할당할 주문용 스크린 번호
        ###############

        ###변수 모음
        self.account_num = None
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        self.portfolio_stock_dict = {}
        ##################

        ###계좌 관련 변수
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        self.deposit = 0  # 예수금
        self.use_money = 0  # 실제 투자에 사용할 금액
        self.use_money_percent = 0.5  # 예수금에서 실제 사용할 비율
        self.output_deposit = 0  # 출력가능 금액
        self.total_profit_loss_money = 0  # 총평가손익금액
        self.total_profit_loss_rate = 0.0  # 총수익률(%)
        ###########################


        ###종목 분석 용
        self.calcul_data= []
        #########################

        #2일차
        self.get_ocx_instance()
        self.event_slots()
        self.signal_login_CommConnect()
        self.get_accout_info()

        #3일차
        self.detail_account_info() #예수금 가져오는 것

        #4일차
        self.detail_account_mystock() #계좌평가 잔고내역 요청

        #5일차
        self.not_concluded_account() #미체결 요청

        #self.calculator_fnc()  # 종목 분석용, 임시용으로 실행

        self.read_code() #저장된 종목들 불러옴

        #7.28
        self.screen_number_setting() #스크린 번호를 겹치지 않게 할당

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")  # 응용 프로그램 제어 가능

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)  # 내가 임의로 만든 slot에다가 결과값을 던져줄것이다.
        self.OnReceiveTrData.connect(self.trdata_slot)  # 실시간 값 받아오기

    def signal_login_CommConnect(self):
        self.dynamicCall("CommConnect()")
        #self.login_event_Loop = QEventLoop()
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

        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString,  QString, int,  QString) ", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)

        # 스크린 번호 : 하나의 그룹을 만들어 준다. TR요청 할 때마다 스크린 번호를 기입을 해 줄 건데, 같은 번호끼리 모인다(200개까지가능)
        # 스크린 번호 1개당 100개의 요청 가능

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()  # 동시성 처리 작업 (이벤트 루프안의 큐나 콜백 부분으로 요청 작업이 들어간다.)

    def detail_account_mystock(self, sPrevNext="0"):
        print("계좌평가 잔고내역 요청 연속조회 %s" % sPrevNext)
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString,  QString, int,  QString) ", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)


        self.detail_account_info_event_loop.exec_()

    def not_concluded_account(self, sPrevNext="0"):
        print("미체결 내역 조회")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.dynamicCall("CommRqData(QString,  QString, int,  QString) ", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)
        print("미체결 내역 조회2")
        self.detail_account_info_event_loop.exec_()
        print("미체결 내역 조회3")

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

            #싱글내역

            total_buy_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0,"총매입금액")
            self.total_buy_money = int(total_buy_money)
            total_profit_loss_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName,0, "총평가손익금액")
            self.total_profit_loss_money = int(total_profit_loss_money)
            total_profit_loss_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName,  0, "총수익률(%)")
            self.total_profit_loss_rate = float(total_profit_loss_rate)
            #self.logging.logger.debug("계좌평가잔고내역요청 싱글데이터 : %s - %s - %s" % (total_buy_money, total_profit_loss_money, total_profit_loss_rate))

            #멀티 내역
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            for i in range(rows):

                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")  # 출력 : A039423 // 알파벳 A는 장내주식, J는 ELW종목, Q는 ETN종목
                code = code.strip()[1:]
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"종목명")  # 출럭 : 한국기업평가
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")  # 보유수량 : 00000000000001
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"매입가")  # 매입가 : 000000000054100
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"수익률(%)")  # 수익률 : -000000001.94
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"현재가")  # 현재가 : 000000003450
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName,i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

                #self.logging.logger.debug("종목코드: %s - 종목명: %s - 보유수량: %s - 매입가:%s - 수익률: %s - 현재가: %s" % ( code, code_nm, stock_quantity, buy_price, learn_rate, current_price))

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

            #self.logging.logger.debug("sPreNext : %s" % sPrevNext)
                #print("계좌에 가지고 있는 종목은 %s " % learn_rate)
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
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,  "주문상태")  # 접수,확인,체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분")  # -매도, +매수, -매도정정, +매수정정
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"미체결수량")
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

                print("미체결 종목 : %s" % self.not_account_stock_dict[order_no])
                #self.logging.logger.debug("미체결 종목 : %s " % self.not_account_stock_dict[order_no])
            self.detail_account_info_event_loop.exit()

        elif sRQName ==  "주식일봉차트조회":

            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("%s 일봉데이터 요청" % code)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print("데이터 일수 %s" % cnt)

            #한번 조회하면 600일치까지 일봉데이터를 받을 수 있다.
            for i in range(cnt): #[0...,599]
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())

            #print(self.calcul_datㅌa)
            #print(len(self.calcul_data))


            if sPrevNext == "2":
                self.day_kiwoom_db(code=code, sPrevNext = sPrevNext)
            else:

                print("총 일수 %s" %len(self.calcul_data))
                # 120일 이평선을 그릴만큼의 데이터가 있는지 체크
                pass_success = False
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False
                else:
                    #120일 이상 되면
                    pass_success = True

                    total_price = 0
                    for value in self.calcul_data[:120]: # 오늘부터 199일까지[오늘,하루전,이틀전,,,,,119일전]
                        total_price += int(value[1]) #120의 종가를 다 더한다.

                    moving_average_price = total_price/120

                    #오늘자 주가가 120일 이평선에 걸쳐있는지 확인
                    bottom_stock_price = False
                    check_price = None

                    if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(self.calcul_data[0][6]):
                        print("오늘 주가 120이평선에 걸쳐있는 것 확인")
                        bottom_stock_price = True
                        check_price = int(self.calcul_data[0][6])

                    #과거 일봉들이 120일 이평선보다 밑에 있는지 확인,
                    #그렇게 확인을 하다가 일봉이 120일 이평선보다 위에 있으면 계산 진행
                    prev_price = None #과거의 일봉 저가
                    if bottom_stock_price == True:
                        moving_average_price_prev = 0
                        price_top_moving = False
                        #56회 14:22 참고
                        idx = 1
                        while True:
                            if len(self.calcul_data[idx:]) < 120: #120일치가 있는지 계속 확인
                                print("120일치가 없음!")
                                break
                            total_price = 0
                            for value in self.calcul_data[idx:120+idx]:
                                total_price += int(value[1])
                            moving_average_price_prev = total_price /120

                            if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <=20:
                                print("20일 동안 주가가 120일 이평선과 같거나 위에 있으면 조건 통과 못함")
                                price_top_moving = False
                                break

                            elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx > 20:
                                print("120일 이평선 위에 있는 일봉 확인됨")
                                price_top_moving = True
                                prev_price = int(self.calcul_data[idx][7])
                                break

                            idx +=1

                        #해당 부분 이평선이 가장 최근 일자의 이평선 가격보다 낮은지 확인
                        if price_top_moving == True:
                            if moving_average_price > moving_average_price_prev and check_price > prev_price:
                                print("포착된 이평선의 가격이 오늘자(최근일자) 이평선 가격보다 낮은 것 확인됨")
                                print("포착된 부분의 일봉 저가가 오늘자 일봉의 고가보다 낮은지 확인됨")
                                pass_success = True

                if pass_success == True:
                    print("조건부 통과됨")

                    code_nm = self.dynamicCall("GetMasterCodeName(Qstring)", code)

                    f = open("files/condition_stock.txt", "a", encoding="utf8") #a는 이어쓰기 / w를 덮어쓰기
                    f.write("%s\t%s\t%s\n" %(code,code_nm, str(self.calcul_data[0][1])))
                    f.close()
                elif pass_success == False:
                    print("조건부 통과 못함")

                self.calcul_data.clear()
                self.calculator_event_loop.exit()

    def get_code_list_by_market(self, market_code): #시장에서 code를 받아 오기 위해
        '''
        종목 코드를 반환환
       :param market_code:
        :return:
        [시장구분값]
          0 : 장내
          10 : 코스닥
          3 : ELW
          8 : ETF
          50 : KONEX
          4 :  뮤추얼펀드
          5 : 신주인수권
          6 : 리츠
          9 : 하이얼펀드
          30 : K-OTC
        '''
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        #print(code_list)
        #code_list = code_list.split(";")[:-1] #처음부터 끝까지
        code_list = code_list.split(";")[:5] #처음부터 5개만
        return code_list


    def calculator_fnc(self):
        '''
        종목 분석용 함수
        :return:
        '''
        code_list = self.get_code_list_by_market("10")
        print("코스닥 갯수 %s" % len(code_list)) #1417

        for idx, code in enumerate(code_list):

            #스크린 번호를 한번이라도 요청하면 그룹이 만들어 진 것 ->그래서 끊어주는 건 개인의 선택
            self.dynamicCall("DisconnectRealData(QString)",self.screen_calculation_stock)

            print("%s / %s : KOSDAQ Stock Code : %s is updating..." %(idx +1, len(code_list),code))
            #print("%s / %s : KOSDAQ Stock Code : %s is updating..." % (idx + 1, 10, code))
            self.day_kiwoom_db(code=code)

    #일봉 가져오기
    def day_kiwoom_db(self, code = None, date = None, sPrevNext = "0"):

        QTest.qWait(3600) #3.6초 delay - 500~700
        #프로세스의 동작을 멈추지 않고 요청되는 동작을 3.6초 지연
        #기타 방법은 프로세스까지 멈추게 한다. 그러면 연길이 끊겨버림

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None: #빈 값이 아닐 경우 기준 일자 입력
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock) # Tr서버로 전송 - Transaction
        self.calculator_event_loop.exec()



    def read_code(self):
        if os.path.exists("files/condition_stock.txt") : #true
            f = open("files/condition_stock.txt", "r", encoding="utf8")

            lines = f.readlines()
            for line in lines:
                if line != "":
                    ls = line.split("\t") #["230923", "종목명", "현재가\n"]

                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = int(ls[2].split("\n")[0])
                    stock_price = abs(stock_price) #절대값 처리

                    self.portfolio_stock_dict.update({stock_code:{"종목명": stock_name, "현재가":stock_price}})
            f.close()
            print(self.portfolio_stock_dict)

    def screen_number_setting(self):
        screen_overwrite = []

        #계좌평가잔고내역에 있는 종목들
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #미체결에 있는 종목들
        for order_number in self.not_account_stock_dict.keys():
            code = self.not_account_stock_dict[order_number]['종목코드']

            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #포트폴리오에 담겨있는 종목들
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)


        #스크린번호 할당
        cnt = 0
        for code in screen_overwrite:

            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1 #개당 종목코드 50개씩 할당해주겟다는 뜻
                self.screen_real_stock = str(temp_screen)

            if (cnt % 50) ==0 :
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({"스크린번호":str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호":str(self.screen_meme_stock)})

            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({code:{"스크린번호":str(self.screen_real_stock)}})

            cnt += 1
        print(self.portfolio_stock_dict)