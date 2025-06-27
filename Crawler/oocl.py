# # CAPTCHA 퍼즐 맞추기 시스템있음. 로직 수행 금지  ###########


# 선사링크 : https://www.oocl.com/eng/ourservices/eservices/trackandtrace/Pages/default.aspx
# 얘네 쿠키 허용해달라는 팝업 뜨는 경우가 있음, 이로 인해 에러가 발생할 수도 있음.
# 선박 리스트 : ["XYT - XIN YAN TAI" , "WAN HAI 335"]
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
        except Exception:
            print('쿠키 허용 버튼이 없거나 이미 처리됨')

        # 2. vessel name 입력 및 조회 버튼 클릭 예시
        vessel_name_list = ["XYT - XIN YAN TAI", "WAN HAI 335"]
        for vessel_name in vessel_name_list:
            # 입력창이 활성화 될 때까지 대기
            vessel_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="VESSEL_NAME"]')))
            vessel_input.clear()
            vessel_input.send_keys(vessel_name)
            print(f"'{vessel_name}' 입력 완료")

            # 자동완성/입력 반영 등 추가 대기가 필요할 경우, 아래처럼 해당 요소가 채워질 때까지 기다릴 수 있습니다
            wait.until(lambda d: vessel_input.get_attribute("value") == vessel_name)

            # submit 버튼이 활성화 될 때까지 대기 후 클릭
            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="vessel_btn"]')))
            submit_btn.click()
            print(f"'{vessel_name}' 조회 버튼 클릭 완료")

            # 결과 페이지(또는 결과 영역)가 나타날 때까지 대기
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="resultPanel"]')), message=f"{vessel_name} 결과 대기")
                print(f"'{vessel_name}' 결과 로딩 완료")
            except Exception as e:
                print(f"'{vessel_name}' 결과 로딩 실패: {e}")

            # 다음 선박명을 위해 검색화면으로 복귀 (예: driver.back() 등)
            driver.back()
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="VESSEL_NAME"]')))

        self.Close()
