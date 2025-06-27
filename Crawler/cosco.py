# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/06/27
# 선사링크 : "https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByVesselName"  -> 한국 홈페이지는 조회 X.  본사랑 다름
# 공동운항 선박 리스트 : "XIN NAN SHA", "XIN RI ZHAO", "XIN WU HAN", "XIN FANG CHENG"
# 추가 정보 : Cosco는 일반 크롤링 접근 막아놨음.  user-agent 필수. __init__ 코드 확인.

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
import tabula
import os
import glob
import pandas as pd
from datetime import datetime

class Cosco_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        # 하위폴더명 = py파일명(소문자)
        self.subfolder_name = self.__class__.__name__.replace("_crawling", "").lower()
        self.download_dir = os.path.join(self.base_download_dir, self.subfolder_name)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        # 크롬 옵션에 하위폴더 지정 (드라이버 새로 생성 필요)
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        self.set_user_agent(chrome_options)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        prefs = {"download.default_directory": self.download_dir}
        chrome_options.add_experimental_option("prefs", prefs)
        # 기존 드라이버 종료 및 새 드라이버로 교체
        self.driver.quit()
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def run(self):
        # TARGET 페이지로 바로 접속
        self.Visit_Link("https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByVesselName")
        driver = self.driver
        wait = self.wait

        # 입력창 찾기
        input_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[1]/div/div/div/div[1]/input'
        vessel_input = wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
        vessel_list = ["XIN NAN SHA", "XIN RI ZHAO", "XIN WU HAN", "XIN FANG CHENG"]

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

            # 조회 시, 새 웹페이지가 떠서 선박 스케줄 스크래핑 후 다시 이전 페이지로 가서 루핑 돌려야할 때의 코드.
            time.sleep(2)
            original_window = driver.current_window_handle
            all_windows = driver.window_handles

            for handle in all_windows:
                if handle != original_window:
                    driver.switch_to.window(handle)
                    break

             # PDF 다운로드 버튼 클릭
            pdf_btn_xpath = '//*[@id="downloadSaislingSchedule"]/div[6]/p/span[3]/i'
            pdf_button = wait.until(EC.element_to_be_clickable((By.XPATH, pdf_btn_xpath)))
            pdf_button.click()
            print("PDF 다운로드 버튼 클릭")

            # 파일 다운로드 대기 (충분히 여유를 줘야 함, 예: 5초)
            time.sleep(5)

            # 파일명 세팅한 코드  (스케줄 데이터 파일 명명 규칙 예시  -> 20250627XIN_NAN_HAI)
            today_str = datetime.now().strftime("%Y%m%d")
            vessel_filename = vessel_name.replace(" ", "_")
            base_filename = f"{today_str}{vessel_filename}"

            # ScheduleData 폴더에서 최신 PDF 파일 찾기
            pdf_files = glob.glob(os.path.join(self.download_dir, "*.pdf"))
            if not pdf_files:
                print("PDF 파일이 없습니다.")
                continue
            latest_pdf = max(pdf_files, key=os.path.getctime)
            print(f"다운로드된 PDF: {latest_pdf}")

            # 원하는 파일명으로 PDF 파일명 변경
            new_pdf_path = os.path.join(self.download_dir, f"{base_filename}.pdf")
            os.rename(latest_pdf, new_pdf_path)
            print(f"PDF 파일명 변경: {new_pdf_path}")

            # PDF  엑셀 변환 (엑셀도 같은 이름으로)
            excel_path = os.path.join(self.download_dir, f"{base_filename}.xlsx")
            dfs = tabula.read_pdf(new_pdf_path, pages='all', multiple_tables=True)
            with pd.ExcelWriter(excel_path) as writer:
                for idx, df in enumerate(dfs):
                    df.to_excel(writer, sheet_name=f"Sheet{idx+1}", index=False)
            print(f"엑셀로 변환 완료: {excel_path}")

        self.Close()