from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.log_class import *


class Account(QAxWidget):
    def __init__(self):
        super().__init__()
        self.logging = Logging()
        self.account_num = None

        # 예수금 요청용 이벤트루프
        self.detail_account_info_event_loop = QEventLoop()

        # OCX 방식을 파이썬에 사용할 수 있게 변환해 주는 함수
        self.get_ocx_instance()
        # 계좌번호 세팅
        self.set_account_number()

    def get_ocx_instance(self):
        # 레지스트리에 저장된 api 모듈 불러오기
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def set_account_number(self):
        # 계좌번호 반환
        account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        account_num = account_list.split(';')[:-1]

        self.account_num = account_num

    def get_account_number(self):
        return self.account_num
