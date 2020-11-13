from PyQt5.QtCore import *


class Account:
    def __init__(self, ocx):
        self.ocx = ocx

        self.account_number_list = None

        # 요청 스크린 번호
        self.screen_my_info = "2000"  # 계좌 관련한 스크린 번호

        # 예수금 요청용 이벤트루프
        self.account_info_event_loop = QEventLoop()

    def set_account_number(self):
        # 계좌번호 반환
        account_list = self.ocx.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        # account_num = account_list.split(';')[:-1]
        account_num = account_list.split(';')[:-1]

        self.account_number_list = account_num

    def get_account_number(self):
        self.set_account_number()
        return self.account_number_list
