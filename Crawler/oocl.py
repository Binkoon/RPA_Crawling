# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/07/03
# 선사링크 : https://www.oocl.com/eng/ourservices/eservices/trackandtrace/Pages/default.aspx
# 얘네 쿠키 허용해달라는 팝업 뜨는 경우가 있음, 이로 인해 에러가 발생할 수도 있음.
# 선박 리스트 : ["XYT - XIN YAN TAI" , "WJK - WAN HAI 335"]
# 추가 정보 : CAPTCHA 퍼즐 슬라이더 기능 있음. 뚫는 방법은 하기 절차 참고
"""
1. https://2captcha.com/2captcha-api  접속
2. 회원가입 후, 로그인
3. 2captcha API KEY 발급
4. 이미지 캡처 후, 2captcha에게 보내면  알아서 슬라이더 움직여줌.
5. 사진과 함께 자세한 설명은 [운항팀] 공동사 스케줄 RPA 개발 -> 02. 기획 & 매니징 자료 -> [Python] 웹크롤링 개발표준 가이드 ver 1.0의 부록 C를 참고
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from .base import ParentsClass

class OOCL_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        
    def run(self):
        # 0. 선사 링크 접속
        self.Visit_Link('https://www.oocl.com/eng/ourservices/eservices/trackandtrace/Pages/default.aspx')
        driver = self.driver
        wait = self.wait

        # 1. 쿠키 허용 버튼이 있으면 클릭, 없으면 무시
        try:
            allow_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="allowAll"]'))
            )
            allow_btn.click()
            print('쿠키 허용 버튼 클릭 완료')
        except Exception as e:
            print('쿠키 허용 버튼이 없거나 이미 처리됨')

        # 2. vessel name 입력 및 조회 버튼 클릭 예시
        vessel_name_list = ["XYT - XIN YAN TAI", "WJK - WAN HAI 335"]
        for vessel_name in vessel_name_list:
            pass

        self.Close()
