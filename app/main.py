from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from login.login import *
from account.account import *
from config.log_class import *


class Main(QAxWidget):
    def __init__(self):
        super().__init__()
        self.logging = Logging()

        self.login = Login()
        self.account = Account()

        self.logging.logger.debug("계좌번호 : %s" % self.account.get_account_number())
