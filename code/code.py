class Code:
    def __init__(self, ocx):
        self.ocx = ocx

    def get_master_code_name(self, code):
        """
        종목코드에 대한 종목명을 얻는 메서드
        :param code: 종목코드
        :return: 종목명
        """
        data = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
        return data

    def get_master_last_price(self, code):
        """
        종목코드의 전일가를 반환하는 메서드
        :param code: 종목코드
        :return: 전일가
        """
        data = self.ocx.dynamicCall("GetMasterLastPrice(QString)", code)
        return int(data)
