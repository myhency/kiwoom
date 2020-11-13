from config.log_class import *


class Condition:
    def __init__(self, ocx, condition_name, get_condition_search_result):
        self.ocx = ocx
        self.condition_name = condition_name
        self.get_condition_search_result = get_condition_search_result
        # logger 인스턴스 설정
        self.logging = Logging()

        # 조건식 이벤트 시그널 / 슬롯
        self.condition_event_slot()

        # 조건식 로딩 하기
        self.signal_condition()

    def signal_condition(self):
        self.ocx.dynamicCall("GetConditionLoad()")

    def condition_slot(self, lRet, sMsg):
        if lRet == 1:
            self.logging.logger.info("조건식 로딩 성공")
            self.logging.logger.info("호출결과 메시지 %s" % sMsg)
        else:
            self.logging.logger.error("조건식 로딩 실패")

        condition_name_list = self.ocx.dynamicCall("GetConditionNameList()")
        # self.logging.logger.debug("HTS의 조건식 이름 가져오기 %s" % condition_name_list)

        condition_name_list = condition_name_list.split(";")[:-1]

        for unit_condition in condition_name_list:
            index = unit_condition.split("^")[0]
            index = int(index)
            condition_name = unit_condition.split("^")[1]

            # self.logging.logger.debug("조건식 분리 번호: %s, 이름: %s" % (index, condition_name))

            if condition_name == self.condition_name:
                '''
                SendCondition(
                    BSTR strScrNo,          // 화면번호
                    BSTR strConditionName,  // 조건식 이름
                    int nIndex,             // 조건명 인덱스
                    int nSearch             // 조회구분, 0:조건검색, 1:실시간 조건검색
                )
                '''
                ok = self.ocx.dynamicCall(
                    "SendCondition(QString, QString, int, int)",
                    "0156",
                    condition_name,
                    index,
                    1
                )
                if ok == 1:
                    self.logging.logger.info("%s 조건검색 조회 성공" % condition_name)
                else:
                    self.logging.logger.error("%s 조건검색 조회 실패" % condition_name)

    def condition_tr_slot(self, sScrNo, strCodeList, strConditionName, index, nNext):
        """
        OnReceiveTrCondition(
          BSTR sScrNo,              // 화면번호
          BSTR strCodeList,         // 종목코드 리스트
          BSTR strConditionName,    // 조건식 이름
          int nIndex,               // 조건명 인덱스
          int nNext                 // 연속조회 여부
        )
        조건검색 요청으로 검색된 종목코드 리스트를 전달하는 이벤트입니다.
        종목코드 리스트는 각 종목코드가 ';'로 구분되서 전달됩니다.
        """
        self.logging.logger.debug("화면번호: %s, " % sScrNo)
        self.logging.logger.debug("종목코드 리스트: %s, " % strCodeList)
        self.logging.logger.debug("조건식 이름: %s, " % strConditionName)
        self.logging.logger.debug("조건식 인덱스: %s, " % index)
        self.logging.logger.debug("연속조회: %s" % nNext)

        code_list = strCodeList.split(";")[:-1]
        # self.logging.logger.debug("종목 코드 리스트 %s" % code_list)
        self.get_condition_search_result(code_list)

    def condition_real_slot(self, strCode, strType, strConditionName, strConditionIndex):
        """
        OnReceiveRealCondition(
          BSTR strCode,             // 종목코드
          BSTR strType,             //  이벤트 종류, "I":종목편입, "D", 종목이탈
          BSTR strConditionName,    // 조건식 이름
          BSTR strConditionIndex    // 조건명 인덱스
        )
        실시간 조건검색 요청으로 신규종목이 편입되거나 기존 종목이 이탈될때 마다 호출됩니다.
        """
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

    def condition_event_slot(self):
        self.logging.logger.debug("조건검색")
        self.ocx.OnReceiveConditionVer.connect(self.condition_slot)
        self.ocx.OnReceiveTrCondition.connect(self.condition_tr_slot)
        self.ocx.OnReceiveRealCondition.connect(self.condition_real_slot)
