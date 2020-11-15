from config.kiwoomType import *
from config.log_class import *


class RealTime:
    def __init__(
            self,
            ocx
    ):
        self.realType = RealType()
        self.ocx = ocx

        # 실시간 이벤트 시그널 / 슬롯 연결
        self.real_event_slot()

    def real_event_slot(self):
        self.ocx.OnReceiveRealData.connect(self.realdata_slot)  # 실시간 이벤트 연결

    def realdata_slot(self, sCode, sRealType, sRealData):
        """
        GetCommRealData(
          BSTR strCode,   // 종목코드
          long nFid   // 실시간 타입에 포함된FID
        )
        """
