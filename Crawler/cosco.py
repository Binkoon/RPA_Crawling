# Cosco는 일반 크롤링 접근 막아놨음.  user-agent 쓰셈. __init__ 코드 확인.

# 선사링크 : "https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByVesselName"  -> 한국 홈페이지는 조회 X.  본사랑 다름
# 선박 리스트 : "XIN NAN SHA", "XIN RI ZHAO", "XIN WU HAN", "XIN FANG CHENG"

################# User-agent 모듈 ###############
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
############### 셀레니움 기본 + time #####
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
######## 부모클래스
from .base import ParentsClass
######### 데이터 저장
import os

class Cosco_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        chrome_options = Options()

        # 다운로드 경로 지정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        download_dir = os.path.join(base_dir, "..", "Schedule_Data")
        download_dir = os.path.abspath(download_dir)
        prefs = {"download.default_directory": download_dir}
        chrome_options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(options=chrome_options)

    def run(self):
        # TARGET 페이지로 바로 접속
        self.Visit_Link("https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByVesselName")
        driver = self.driver
        wait = WebDriverWait(driver, 20)

        # 입력창 찾기
        input_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[1]/div/div/div/div[1]/input'
        vessel_input = wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))

        vessel_list = ["XIN NAN SHA"]

        for vessel_name in vessel_list:
            vessel_input.clear()
            vessel_input.click()
            vessel_input.send_keys(vessel_name)
            print(f"입력: {vessel_name}")
            time.sleep(1)  # 자동완성 등 반응 대기

            # 자동완성 드롭다운 항목 클릭
            dropdown_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[1]/div/div/div[1]/div[2]/ul[2]/div/li'
            dropdown_item = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
            dropdown_item.click()
            print("자동완성 리스트 클릭")

            # Search 버튼 클릭
            search_btn_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[2]/button'
            search_button = wait.until(EC.element_to_be_clickable((By.XPATH, search_btn_xpath)))
            search_button.click()
            print("Search 버튼 클릭")

            # 결과 로딩 대기 (필요시)
            time.sleep(2)

             # PDF 다운로드 버튼 클릭
            pdf_btn_xpath = '//*[@id="downloadSaislingSchedule"]/div[6]/p/span[3]/i'
            pdf_button = wait.until(EC.element_to_be_clickable((By.XPATH, pdf_btn_xpath)))
            pdf_button.click()
            print("PDF 다운로드 버튼 클릭")

            # 파일 다운로드 대기 (충분히 여유를 줘야 함, 예: 5초)
            time.sleep(5)

        self.Close()