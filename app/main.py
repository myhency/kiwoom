import os
import sys

from datetime import date

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
        # Config 설정
        with open('./config/app.config.json', 'r') as f:
            self.config = json.load(f)

        # 요청 스크린 번호
        self.screen_my_info = "2000"  # 계좌 관련한 스크린 번호
        self.screen_start_stop_real = "1000"  # 장 시작/종료 실시간 스크린번호
        self.screen_code_info = "3000"

        # 로그인 요청용 이벤트루프
        self.login_event_loop = QEventLoop()
        self.code_event_loop = QEventLoop()

        # OCX 방식을 파이썬에 사용할 수 있게 변환해 주는 오브젝트
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")

        # 키움과 연결하기 위한 시그널 / 슬롯 모음
        self.event_slots()

        # telegram test message 보내기
        self.myBot.send_message_to_my_bot(str(datetime.now().strftime('%Y/%m/%d %H:%M')))
        # 로그인 요청 시그널 포함
        self.signal_login_commConnect()

        self.my_condition = {}
        self.condition_tr_result = []
        self.condition_real_result = {}

        # 조건검색 시작하기
        self.condition = Condition(
            self.ocx,
            self.set_condition_list,
            self.set_code_list,
            self.set_realtime_code
        )

        self.condition.sendCondition(
            self.screen_code_info,
            self.my_condition['name'],
            self.my_condition['key'],
            1
        )

        while True:
            if self.config['CONDITION']:
                break
            if len(self.condition_tr_result) != 0:
                self.logging.logger.debug("condition_tr_result 수신 완료")
                for code in self.condition_tr_result:
                    self.get_code_detail(code)
                break
            else:
                self.logging.logger.debug("condition_tr_result 수신 전")
                continue

        while True:
            if bool(self.condition_real_result):
                self.logging.logger.debug("condition_real_result 수신 완료")
                if self.condition_real_result['type'] == "I":
                    self.get_code_detail(self.condition_real_result['code'])
                    self.condition_real_result = {}

        # 코드 정보 받아오기 인스턴스
        # self.code_info = Code(self.ocx)

    def set_realtime_code(self, code, event):
        self.logging.logger.debug("[set_realtime_code]")
        self.logging.logger.debug("실시간 조건검색 결과: 종목코드 %s, 종목편출입: %s" % (code, event))
        self.condition_real_result.update({
            "code": code,
            "type": event
        })

    def set_condition_list(self, condition_list):
        self.logging.logger.debug("[set_condition_list]")
        self.logging.logger.info("조건식 리스트: %s" % condition_list)
        for key in condition_list.keys():
            if condition_list[key] == "도지돌파":
                self.my_condition = {
                    "key": key,
                    "name": condition_list[key]
                }

    def set_code_list(self, code_list):
        if self.config['CONDITION']:
            return
        else:
            self.logging.logger.debug("[set_code_list]")
            self.condition_tr_result = code_list

    def get_code_detail(self, code, sPrevNext="0"):
        self.logging.logger.debug("get_code_detail")
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        # Tr서버로 전송 -Transaction
        self.ocx.dynamicCall(
            "CommRqData(QString, QString, int, QString)",
            "주식기본정보요청",
            "opt10001",
            sPrevNext,
            self.screen_code_info
        )
        self.code_event_loop.exec_()

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        self.logging.logger.debug("trdata_slot")
        if sRQName == "주식기본정보요청":
            code = self.get_comm_data(sTrCode, sRQName, 0, "종목코드")
            code_name = self.get_comm_data(sTrCode, sRQName, 0, "종목명")
            current_price = self.get_comm_data(sTrCode, sRQName, 0, "현재가")
            ratio_by_yesterday = self.get_comm_data(sTrCode, sRQName, 0, "등락율")
            begin_price = self.get_comm_data(sTrCode, sRQName, 0, "시가")
            high_price = self.get_comm_data(sTrCode, sRQName, 0, "고가")
            low_price = self.get_comm_data(sTrCode, sRQName, 0, "저가")

            current_price = format(int(str(abs(int(current_price)))), ",")
            begin_price = format(int(str(abs(int(begin_price)))), ",")
            high_price = format(int(str(abs(int(high_price)))), ",")
            low_price = format(int(str(abs(int(low_price)))), ",")

            self.myBot.send_message_to_my_bot(
                "[" + code + "]" + code_name + "\n" +
                "현재가 : " + current_price + "\n" +
                "등락율 : " + ratio_by_yesterday + "%" + "\n" +
                "시가 : " + begin_price + "\n" +
                "고가 : " + high_price + "\n" +
                "저가 : " + low_price + "\n" +
                "https://kr.tradingview.com/chart/?symbol=KRX%3A" + code
            )

            self.stop_screen_cancel(self.screen_code_info)
        else:
            self.stop_screen_cancel(self.screen_code_info)

        self.code_event_loop.exit()

    def get_comm_data(self, sTrCode, sRQName, index, name):
        """
        GetCommData(
          BSTR strTrCode,       // TR 이름
          BSTR strRecordName,   // 레코드이름
          long nIndex,          // TR반복부
          BSTR strItemName      // TR에서 얻어오려는 출력항목이름
        )
        OnReceiveTRData()이벤트가 호출될때 조회데이터를 얻어오는 함수입니다.
        이 함수는 반드시 OnReceiveTRData()이벤트가 호출될때 그 안에서 사용해야 합니다.
        :param sTrCode:
        :param sRQName:
        :param index:
        :param name:
        :return:
        """
        ret = self.ocx.dynamicCall(
            "GetCommData(QString, QString, int, QString)",
            sTrCode,
            sRQName,
            index,
            name
        )
        return ret.strip()

    def signal_login_commConnect(self):
        self.ocx.dynamicCall("CommConnect()")  # 로그인 요청 시그널

        self.login_event_loop.exec_()  # 이벤트루프 실행

    def login_slot(self, err_code):
        self.logging.logger.debug(errors(err_code)[1])

        # 로그인 처리가 완료됐으면 이벤트 루프를 종료한다.
        self.login_event_loop.exit()

    # 송수신 메세지 get
    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        self.logging.logger.debug("스크린: %s, 요청이름: %s, tr코드: %s --- %s" % (sScrNo, sRQName, sTrCode, msg))

        # self.logging.logger.debug("계좌번호 : %s" % self.account.get_account_number())
        # self.logging.logger.debug("계좌번호 : %s" % self.account.get_account_number())

    def event_slots(self):
        self.ocx.OnEventConnect.connect(self.login_slot)  # 로그인 관련 이벤트
        self.ocx.OnReceiveMsg.connect(self.msg_slot)
        self.ocx.OnReceiveTrData.connect(self.trdata_slot)  # 트랜잭션 요청 관련 이벤트

    def stop_screen_cancel(self, sScrNo=None):
        # 스크린번호 연결 끊기
        self.ocx.dynamicCall("DisconnectRealData(QString)", sScrNo)

