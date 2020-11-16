from config.log_class import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
from mybot.mybot import *


class Condition:
    def __init__(
            self,
            ocx,
            # condition_name,
            # send_condition,
            set_condition_list,
            set_code_list,
            set_realtime_code
    ):
        self.ocx = ocx
        # self.condition_name = None
        # self.send_condition = send_condition
        self.set_condition_list = set_condition_list
        self.set_code_list = set_code_list
        self.set_realtime_code = set_realtime_code
        # logger 인스턴스 설정
        self.logging = Logging()

        self.msg = ''

        # self.myBot = MyBot()

        self.screen_code_info = "3000"

        self.condition_event_loop = QEventLoop()
        # self.code_event_loop = QEventLoop()

        # 조건식 이벤트 시그널 / 슬롯
        self.condition_event_slot()

        # 조건식 로딩 하기
        # self.signal_condition()
        self.getConditionLoad()

    def get_master_code_name(self, code):
        self.logging.logger.debug("[get_master_code_name]")
        code_name = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def receiveConditionVer(self, receive, msg):
        """
        getConditionLoad() 메서드의 조건식 목록 요청에 대한 응답 이벤트
        :param receive: int - 응답결과(1: 성공, 나머지 실패)
        :param msg: string - 메세지
        """
        self.logging.logger.debug("[receiveConditionVer]")
        try:
            if not receive:
                return

            self.condition = self.getConditionNameList()
            self.logging.logger.debug("조건식 개수: %s" % len(self.condition))
            condition_list = self.condition
            self.set_condition_list(condition_list)

            # for key in self.condition.keys():
            #     print("조건식: ", key, ": ", self.condition[key])
            #     # print("key type: ", type(key))

        except Exception as e:
            print(e)

        finally:
            self.conditionLoop.exit()

    def receiveTrCondition(self, screenNo, codes, conditionName, conditionIndex, inquiry):
        """
        (1회성, 실시간) 종목 조건검색 요청시 발생되는 이벤트
        :param screenNo: string
        :param codes: string - 종목코드 목록(각 종목은 세미콜론으로 구분됨)
        :param conditionName: string - 조건식 이름
        :param conditionIndex: int - 조건식 인덱스
        :param inquiry: int - 조회구분(0: 남은데이터 없음, 2: 남은데이터 있음)
        """

        self.logging.logger.debug("[receiveTrCondition]")
        try:
            if codes == "":
                return
            codeList = codes.split(';')
            del codeList[-1]

            self.logging.logger.debug("종목개수: %s" % len(codeList))
            self.logging.logger.debug(codeList)

            self.set_code_list(codeList)

        finally:
            self.logging.logger.debug("receiveTrCondition finally")
            self.conditionLoop.exit()

    def receiveRealCondition(self, code, event, conditionName, conditionIndex):
        self.logging.logger.debug("[receiveRealCondition]")
        """
        실시간 종목 조건검색 요청시 발생되는 이벤트
        :param code: string - 종목코드
        :param event: string - 이벤트종류("I": 종목편입, "D": 종목이탈)
        :param conditionName: string - 조건식 이름
        :param conditionIndex: string - 조건식 인덱스(여기서만 인덱스가 string 타입으로 전달됨)
        """
        # msg = "{} {} {}\n".format("종목편입" if event == "I" else "종목이탈", code, self.get_master_code_name(code))
        # self.msg += msg
        self.set_realtime_code(code, event)

    def getConditionLoad(self):
        self.logging.logger.debug("[getConditionLoad]")
        """ 조건식 목록 요청 메서드 """

        isLoad = self.ocx.dynamicCall("GetConditionLoad()")
        # 요청 실패시
        if not isLoad:
            print("getConditionLoad(): 조건식 요청 실패")

        # receiveConditionVer() 이벤트 메서드에서 루프 종료
        self.conditionLoop = QEventLoop()
        self.conditionLoop.exec_()

    def getConditionNameList(self):
        self.logging.logger.debug("[getConditionNameList]")
        """
        조건식 획득 메서드
        조건식을 딕셔너리 형태로 반환합니다.
        이 메서드는 반드시 receiveConditionVer() 이벤트 메서드안에서 사용해야 합니다.
        :return: dict - {인덱스:조건명, 인덱스:조건명, ...}
        """

        data = self.ocx.dynamicCall("GetConditionNameList()")

        if data == "":
            self.logging.logger.debug("getConditionNameList(): 사용자 조건식이 없습니다.")

        conditionList = data.split(';')
        del conditionList[-1]

        conditionDictionary = {}

        for condition in conditionList:
            key, value = condition.split('^')
            conditionDictionary[int(key)] = value

        return conditionDictionary

    def sendCondition(self, screenNo, conditionName, conditionIndex, isRealTime):
        self.logging.logger.debug("[sendCondition]")
        """
        종목 조건검색 요청 메서드
        이 메서드로 얻고자 하는 것은 해당 조건에 맞는 종목코드이다.
        해당 종목에 대한 상세정보는 setRealReg() 메서드로 요청할 수 있다.
        요청이 실패하는 경우는, 해당 조건식이 없거나, 조건명과 인덱스가 맞지 않거나, 조회 횟수를 초과하는 경우 발생한다.
        조건검색에 대한 결과는
        1회성 조회의 경우, receiveTrCondition() 이벤트로 결과값이 전달되며
        실시간 조회의 경우, receiveTrCondition()과 receiveRealCondition() 이벤트로 결과값이 전달된다.
        :param screenNo: string
        :param conditionName: string - 조건식 이름
        :param conditionIndex: int - 조건식 인덱스
        :param isRealTime: int - 조건검색 조회구분(0: 1회성 조회, 1: 실시간 조회)
        """

        isRequest = self.ocx.dynamicCall("SendCondition(QString, QString, int, int",
                                     screenNo, conditionName, conditionIndex, isRealTime)

        msg = "{} 실행\n".format(conditionName)
        self.msg += msg

        if not isRequest:
            self.logging.logger.debug("sendCondition(): 조건검색 요청 실패")

        # receiveTrCondition() 이벤트 메서드에서 루프 종료
        self.conditionLoop = QEventLoop()
        self.conditionLoop.exec_()

    def sendConditionStop(self, screenNo, conditionName, conditionIndex):

        print("[sendConditionStop]")
        """ 종목 조건검색 중지 메서드 """

        self.ocx.dynamicCall("SendConditionStop(QString, QString, int)", screenNo, conditionName, conditionIndex)
        msg = "{} 중지\n".format(conditionName)

        self.msg += msg

    def signal_condition(self):
        self.ocx.dynamicCall("GetConditionLoad()")
        self.condition_event_loop.exec_()

    def condition_event_slot(self):
        self.logging.logger.debug("조건검색")
        ## 조건검색식 관련 추가
        self.ocx.OnReceiveConditionVer.connect(self.receiveConditionVer)
        self.ocx.OnReceiveTrCondition.connect(self.receiveTrCondition)
        self.ocx.OnReceiveRealCondition.connect(self.receiveRealCondition)

    def stop_screen_cancel(self, sScrNo=None):
        # 스크린번호 연결 끊기
        self.ocx.dynamicCall("DisconnectRealData(QString)", sScrNo)
