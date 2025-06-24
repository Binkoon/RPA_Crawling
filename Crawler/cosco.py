# Cosco는 일반 크롤링 접근 막아놨음.  user-agent 쓰셈. __init__ 코드 확인.

# 선사링크 : "https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByVesselName"  -> 한국 홈페이지는 조회 X.  본사랑 다름
# 선박 리스트 : "XIN NAN SHA", "XIN RI ZHAO", "XIN WU HAN", "XIN FANG CHENG"
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from .base import ParentsClass
import time

class Cosco_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=chrome_options)

    def run(self):
        try:
            # TARGET 페이지로 바로 접속
            self.Visit_Link("https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByVesselName")
            driver = self.driver
            wait = self.wait  # 20초 대기
            print("TARGET 페이지로 직접 접속 완료")
            time.sleep(5)  # 페이지 안정화 대기 강화

            # 팝업 처리 (alert 확인)
            try:
                alert = wait.until(EC.alert_is_present())
                alert_text = alert.text
                print(f"알림 팝업 감지: {alert_text}")
                alert.accept()  # 확인 버튼 클릭
                print("팝업 닫음")
                time.sleep(2)  # 팝업 처리 후 대기
            except:
                print("알림 팝업 없음")

            # 일반 팝업/모달 처리 (예: div 기반)
            try:
                popup_close = wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//button[contains(@class, 'close') or text()='Close' or text()='확인']"
                )))
                popup_close.click()
                print("일반 팝업 닫음")
                time.sleep(2)  # 팝업 처리 후 대기
            except:
                print("일반 팝업 없음")

            # 부모 div (ivu-select) 클릭으로 드롭다운 펼치기
            select_container = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "div.ivu-select"
            )))
            select_container.click()
            print("ivu-select 컨테이너 클릭, 드롭다운 펼침")
            # 드롭다운이 visible 상태로 변경될 때까지 대기
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ivu-select-dropdown")))
            print("드롭다운 활성화 완료")
            time.sleep(2)  # 드롭다운 안정화 대기

            # INPUT 요소 타겟팅 및 값 입력
            vessel_input = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "input[placeholder='sailing_schedule_vessel_search_vessel_name'].ivu-select-input"
            )))
            driver.execute_script("arguments[0].focus();", vessel_input)
            vessel_input.click()
            vessel_input.send_keys("XIN NAN SHA")
            print("선박명 'XIN NAN SHA' 입력")
            time.sleep(2)  # 입력 후 대기

            # Search 버튼 클릭
            search_button = wait.until(EC.element_to_be_clickable((
                By.CLASS_NAME, "btnSearch.ivu-btn"
            )))
            search_button.click()
            print("Search 버튼 클릭")
            time.sleep(3)  # 검색 결과 로드 대기

            # 페이지 로드 대기
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)  # 최종 결과 대기

        except Exception as e:
            print(f"에러 발생: {str(e)}. 현재 페이지 소스 일부: {driver.page_source[:1000]}")
            print("페이지 URL:", driver.current_url)
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='sailing_schedule_vessel_search_vessel_name'].ivu-select-input")
            print(f"CSS Selector 매칭 요소 개수: {len(inputs)}")
            if inputs:
                print(f"첫 번째 요소 속성: {inputs[0].get_attribute('disabled')}, {inputs[0].get_attribute('readonly')}")

        self.Close()