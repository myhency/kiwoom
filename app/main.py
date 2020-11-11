import os
import sys

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.log_class import *
from config.kiwoomType import *
from PyQt5.QtTest import *
from config.errorCode import *


class Main(QAxWidget):
    def __init__(self):
        super().__init__()
        self.realType = RealType()
        self.logging = Logging()

        # 요청 스크린 번호
        self.screen_my_info = "2000"  # 계좌 관련한 스크린 번호
        self.screen_start_stop_real = "1000"  # 장 시작/종료 실시간 스크린번호

        # 로그인 요청용 이벤트루프
        self.login_event_loop = QEventLoop()
        # 예수금 요청용 이벤트루프
        self.detail_account_info_event_loop = QEventLoop()

        # OCX 방식을 파이썬에 사용할 수 있게 변환해 주는 함수
        self.get_ocx_instance()
        # 키움과 연결하기 위한 시그널 / 슬롯 모음
        self.event_slots()
        # 실시간 이벤트 시그널 / 슬롯 연결
        self.real_event_slot()
        # 로그인 요청 시그널 포함
        self.signal_login_commConnect()
        # 계좌번호 세팅
        self.set_account_number()
        # 예수금 세팅
        self.signal_deposit()

        # 장시작 종료 실시간 알림
        self.signal_market_open_time()

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")  # 레지스트리에 저장된 api 모듈 불러오기

    def set_account_number(self):
        # 계좌번호 반환
        account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        # account_num = account_list.split(';')[:-1]
        account_num = account_list.split(';')[0]

        self.account_num = account_num

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")  # 로그인 요청 시그널

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
            "1050"
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
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

            print("value: %s" % value)

            if value == '0':
                self.logging.logger.debug("장 시작 전")

            elif value == '3':
                self.logging.logger.debug("장 시작")

            elif value == "2":
                self.logging.logger.debug("장 종료, 동시호가로 넘어감")

            elif value == "4":
                self.logging.logger.debug("3시30분 장 종료")

                for code in self.portfolio_stock_dict.keys():
                    self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'], code)

                QTest.qWait(5000)

                self.file_delete()
                self.calculator_fnc()

                sys.exit()

    def stop_screen_cancel(self, sScrNo=None):
        self.dynamicCall("DisconnectRealData(QString)", sScrNo) # 스크린번호 연결 끊기

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)  # 로그인 관련 이벤트
        # 트랜잭션 요청 관련 이벤트
        self.OnReceiveTrData.connect(self.trdata_slot)
        self.OnReceiveMsg.connect(self.msg_slot)

    def real_event_slot(self):
        self.OnReceiveRealData.connect(self.realdata_slot)  # 실시간 이벤트 연결
