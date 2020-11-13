import os
import sys

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.log_class import *
from config.kiwoomType import *
from PyQt5.QtTest import *
from config.errorCode import *

from account.account import *
from condition.condition import *
from code.code import *
from mybot.mybot import *

class Main:
    def __init__(self):
        # 실시간 알람 타입 인스턴스 설정
        self.realType = RealType()
        # logger 인스턴스 설정
        self.logging = Logging()
        # telegram 인스턴스 설정
        self.myBot = MyBot()

        # 요청 스크린 번호
        self.screen_my_info = "2000"  # 계좌 관련한 스크린 번호
        self.screen_start_stop_real = "1000"  # 장 시작/종료 실시간 스크린번호

        # 로그인 요청용 이벤트루프
        self.login_event_loop = QEventLoop()

        # OCX 방식을 파이썬에 사용할 수 있게 변환해 주는 오브젝트
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")

        # 키움과 연결하기 위한 시그널 / 슬롯 모음
        self.event_slots()

        # telegram test message 보내기
        self.myBot.send_message_to_my_bot("Test message")
        self.myBot.send_message_to_my_channel("안녕하세요 제임스입니다")
        # 로그인 요청 시그널 포함
        self.signal_login_commConnect()

        # 계좌번호 받아오기
        self.account = Account(self.ocx)
        self.account_number = self.account.get_account_number()
        self.logging.logger.debug(self.account_number)

        self.condition = Condition(self.ocx, "도지돌파", self.get_condition_search_result)

        # 코드 정보 받아오기 인스턴스
        self.code_info = Code(self.ocx)

        # # 예수금 세팅
        # self.signal_deposit()
        # # 장시작 종료 실시간 알림
        # self.signal_market_open_time()
        # # 조건식 로딩 하기
        # self.signal_condition()

    def get_condition_search_result(self, code_list):
        self.logging.logger.info("종목 코드 리스트: %s" % code_list)
        for code in code_list:
            code_name = self.code_info.get_master_code_name(code)
            last_price = self.code_info.get_master_last_price(code)
            self.logging.logger.info("종목명: %s" % code_name)
            self.logging.logger.info("전일종가: %s" % last_price)
            self.logging.logger.info("차트URL: https://kr.tradingview.com/chart/?symbol=KRX%%3A%s" % code)
            self.myBot.send_message_to_my_channel(
                "[" + code + "]" + code_name + "\n" +
                "전일종가 : " + last_price + "\n" +
                "https://kr.tradingview.com/chart/?symbol=KRX%%3A" + code
            )

    def signal_login_commConnect(self):
        self.ocx.dynamicCall("CommConnect()")  # 로그인 요청 시그널

        self.login_event_loop.exec_()  # 이벤트루프 실행

    def signal_deposit(self, sPrevNext="0"):
        self.dynamicCall(
            "SetInputValue(QString, QString)",
            "계좌번호",
            self.account_num
        )
        self.dynamicCall(
            "SetInputValue(QString, QString)",
            "비밀번호",
            self.account_pass
        )
        self.dynamicCall(
            "SetInputValue(QString, QString)",
            "비밀번호입력매체구분",
            "00"
        )
        self.dynamicCall(
            "SetInputValue(QString, QString)",
            "조회구분",
            "1"
        )
        self.dynamicCall(
            "CommRqData(QString, QString, int, QString)",
            "예수금상세현황요청",
            "opw00001",
            sPrevNext,
            self.screen_my_info
        )

        self.detail_account_info_event_loop.exec_()

    def signal_market_open_time(self):
        self.dynamicCall(
            "SetRealReg(QString, QString, QString, QString)",
            self.screen_start_stop_real,
            '',
            self.realType.REALTYPE['장시작시간']['장운영구분'],
            "0"
        )

    # def signal_condition(self):
    #     self.dynamicCall("GetConditionLoad()")

    def login_slot(self, err_code):
        self.logging.logger.debug(errors(err_code)[1])

        # 로그인 처리가 완료됐으면 이벤트 루프를 종료한다.
        self.login_event_loop.exit()

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                sTrCode,
                sRQName,
                0,
                "예수금"
            )
            self.my_deposit = int(deposit)

            self.logging.logger.debug("예수금 : %s" % self.my_deposit)

            self.stop_screen_cancel(self.screen_my_info)

            self.detail_account_info_event_loop.exit()

    # 송수신 메세지 get
    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        self.logging.logger.debug("스크린: %s, 요청이름: %s, tr코드: %s --- %s" % (sScrNo, sRQName, sTrCode, msg))

        # self.logging.logger.debug("계좌번호 : %s" % self.account.get_account_number())
        # self.logging.logger.debug("계좌번호 : %s" % self.account.get_account_number())

    def realdata_slot(self, sCode, sRealType, sRealData):
        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']  # (0:장시작전, 2:장종료전(20분), 3:장시작, 4,8:장종료(30분), 9:장마감)
            value = self.ocx.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

            print("value: %s" % value)

            if value == '0':  # 08:30 ~ 09:00
                self.logging.logger.debug("장 시작 전")
                self.bot.sendMessage(chat_id=self.bot_id, text="장 시작 전")

            elif value == '3':  # 09:00 ~ 15:20
                self.logging.logger.debug("장 시작")
                self.bot.sendMessage(chat_id=self.bot_id, text="장 시작")

            elif value == "2":  # 15:20 ~ 15:30
                self.logging.logger.debug("장 종료, 동시호가로 넘어감")
                self.bot.sendMessage(chat_id=self.bot_id, text="장 종료, 동시호가로 넘어감")

            elif value == "4":  # 15:30
                self.logging.logger.debug("3시30분 장 종료")
                self.bot.sendMessage(chat_id=self.bot_id, text="3시30분 장 종료")

                # for code in self.portfolio_stock_dict.keys():
                #     self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'], code)

                QTest.qWait(5000)

                # self.file_delete()
                # self.calculator_fnc()

                sys.exit()

    def condition_slot(self, lRet, sMsg):
        self.logging.logger.debug("호출 성공 여부 %s, 호출결과 메시지 %s" % (lRet, sMsg))

        condition_name_list = self.ocx.dynamicCall("GetConditionNameList()")
        self.logging.logger.debug("HTS의 조건식 이름 가져오기 %s" % condition_name_list)

        condition_name_list = condition_name_list.split(";")[:-1]

        for unit_condition in condition_name_list:
            index = unit_condition.split("^")[0]
            index = int(index)
            condition_name = unit_condition.split("^")[1]

            self.logging.logger.debug("조건식 분리 번호: %s, 이름: %s" % (index, condition_name))

            # 조회요청 + 실시간 조회
            ok = self.ocx.dynamicCall("SendCondition(QString, QString, int, int)", "0156", condition_name, index, 1)

            self.logging.logger.debug("조회 성공여부 %s" % ok)

    def condition_tr_slot(self, sScrNo, strCodeList, strConditionName, index, nNext):
        self.logging.logger.debug(
            "화면번호: %s, "
            "종목코드 리스트: %s, "
            "조건식 이름: %s, "
            "조건식 인덱스: %s, "
            "연속조회: %s" % (sScrNo, strCodeList, strConditionName, index, nNext))

        code_list = strCodeList.split(";")[:-1]
        self.logging.logger.debug("코드 종목 \n %s" % code_list)

    def condition_real_slot(self, strCode, strType, strConditionName, strConditionIndex):
        self.logging.logger.debug(
            "종목코드: %s, "
            "이벤트종류: %s, "
            "조건식이름: %s, "
            "조건명인덱스: %s" % (strCode, strType, strConditionName, strConditionIndex))

        if strType == "I":
            self.logging.logger.debug(
                "종목코드: %s, "
                "종목편입: %s" % (strCode, strType))
        elif strType == "D":
            self.logging.logger.debug(
                "종목코드: %s, "
                "종목이탈: %s" % (strCode, strType))

    def event_slots(self):
        self.ocx.OnEventConnect.connect(self.login_slot)  # 로그인 관련 이벤트
        # 트랜잭션 요청 관련 이벤트
        self.ocx.OnReceiveTrData.connect(self.trdata_slot)
        self.ocx.OnReceiveMsg.connect(self.msg_slot)

    def real_event_slot(self):
        self.ocx.OnReceiveRealData.connect(self.realdata_slot)  # 실시간 이벤트 연결

    def condition_event_slot(self):
        self.ocx.OnReceiveConditionVer.connect(self.condition_slot)
        self.ocx.OnReceiveTrCondition.connect(self.condition_tr_slot)
        self.ocx.OnReceiveRealCondition.connect(self.condition_real_slot)

    def stop_screen_cancel(self, sScrNo=None):
        # 스크린번호 연결 끊기
        self.ocx.dynamicCall("DisconnectRealData(QString)", sScrNo)

