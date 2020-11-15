class RealType(object):
    SENDTYPE = {
        '거래구분': {
            '지정가': '00',
            '시장가': '03',
            '조건부지정가': '05',
            '최유리지정가': '06',
            '최우선지정가': '07',
            '지정가IOC': '10',
            '시장가IOC': '13',
            '최유리IOC': '16',
            '지정가FOK': '20',
            '시장가FOK': '23',
            '최유리FOK': '26',
            '장전시간외종가': '61',
            '시간외단일가매매': '62',
            '장후시간외종가': '81'
        }
    }

    REALTYPE = {

        '주식체결': {
            '체결시간': 20,
            '현재가': 10, #체결가
            '전일대비': 11,
            '등락율': 12,
            '(최우선)매도호가': 27,
            '(최우선)매수호가': 28,
            '거래량': 15,
            '누적거래량': 13,
            '누적거래대금': 14,
            '시가': 16,
            '고가': 17,
            '저가': 18,
            '전일대비기호': 25,
            '전일거래량대비': 26,
            '거래대금증감': 29,
            '전일거래량대비': 30,
            '거래회전율': 31,
            '거래비용': 32,
            '체결강도': 228,
            '시가총액(억)': 311,
            '장구분': 290,
            'KO접근도': 691,
            '상한가발생시간': 567,
            '하한가발생시간': 568
        },

        '장시작시간': {
            '장운영구분': 215,
            '시간': 20, #(HHMMSS)
            '장시작예상잔여시간':214
        },

        '주문체결': {
            '계좌번호': 9201,
            '주문번호': 9203,
            '관리자사번': 9205,
            '종목코드': 9001,
            '주문업무분류': 912, #(jj:주식주문)
            '주문상태': 913, #(접수, 확인, 체결) (10:원주문, 11:정정주문, 12:취소주문, 20:주문확인, 21:정정확인, 22:취소확인, 90,92:주문거부) #https://bbn.kiwoom.com/bbn.openAPIQnaBbsDetail.do
            '종목명': 302,
            '주문수량': 900,
            '주문가격': 901,
            '미체결수량': 902,
            '체결누계금액': 903,
            '원주문번호': 904,
            '주문구분': 905, #(+매수, -매도, -매도정정, +매수정정, 매수취소, 매도취소)
            '매매구분': 906, #(보통, 시장가등)
            '매도수구분': 907, # 매도(매도정정, 매도취도 포함)인 경우 1, 매수(매수정정, 매수취소 포함)인 경우 2
            '주문/체결시간': 908, #(HHMMSS)
            '체결번호': 909,
            '체결가': 910,
            '체결량': 911,
            '현재가': 10,
            '(최우선)매도호가': 27,
            '(최우선)매수호가': 28,
            '단위체결가': 914,
            '단위체결량': 915,
            '당일매매수수료': 938,
            '당일매매세금': 939,
            '거부사유': 919,
            '화면번호': 920,
            '터미널번호': 921,
            '신용구분(실시간 체결용)': 922,
            '대출일(실시간 체결용)': 923,
        },

        '매도수구분': {
            '1': '매도',
            '2': '매수'
        },

        '잔고': {
            '계좌번호': 9201,
            '종목코드': 9001,
            '종목명': 302,
            '현재가': 10,
            '보유수량': 930,
            '매입단가': 931,
            '총매입가': 932,
            '주문가능수량': 933,
            '당일순매수량': 945,
            '매도매수구분': 946,
            '당일총매도손익': 950,
            '예수금': 951,
            '(최우선)매도호가': 27,
            '(최우선)매수호가': 28,
            '기준가': 307,
            '손익율': 8019
        },

        '주식시세': {
            '현재가': 10,
            '전일대비': 11,
            '등락율': 12,
            '(최우선)매도호가': 27,
            '(최우선)매수호가': 28,
            '누적거래량': 13,
            '누적거래대금': 14,
            '시가': 16,
            '고가': 17,
            '저가': 18,
            '전일대비기호': 25,
            '전일거래량대비(계약,주)': 26,
            '거래대금증감': 29,
            '전일거래량대비(비율)': 30,
            '거래회전율': 31,
            '거래비용': 32,
            '시가총액(억)': 311,
            '상한가발생시간': 567,
            '하한가발생시간': 568
        }
    }