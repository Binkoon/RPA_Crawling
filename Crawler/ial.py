# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/07/02 (완성)
# 선사 링크 : https://www.interasia.cc/Service/Form?servicetype=1
# 선박 리스트 : ["INTERASIA PROGRESS" ,"INTERASIA ENGAGE" , "INTERASIA HORIZON"]

# https://www.interasia.cc/Service/BoatList?ShipName=INTERASIA%20PROGRESS&StartDate=2025-07-01
# https://www.interasia.cc/Service/BoatList?ShipName=INTERASIA%20ENGAGE&StartDate=2025-07-01
# https://www.interasia.cc/Service/BoatList?ShipName=INTERASIA%20HORIZON&StartDate=2025-07-01

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from .base import ParentsClass
import os,time
from datetime import datetime

import pandas as pd

class IAL_Crawling(ParentsClass):
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
        # 0. 선사 홈페이지 접속
        vessel_name_list = ["INTERASIA PROGRESS" ,"INTERASIA ENGAGE" , "INTERASIA HORIZON"]
        today = datetime.today().strftime("%Y-%m-%d")
        driver = self.driver
        wait = self.wait

        for vessel_name in vessel_name_list:
            vessel_param = vessel_name.replace(" ","%20")
            url = f'https://www.interasia.cc/Service/BoatList?ShipName={vessel_param}&StartDate={today}'
            self.Visit_Link(url)

            # 1) 테이블 헤더 가져오기
            thead_xpath = '//*[@id="wrapper"]/main/section[2]/div/div[2]/div[2]/table/thead'
            thead = driver.find_element(By.XPATH, thead_xpath)
            headers = [th.text.strip() for th in thead.find_elements(By.TAG_NAME, "th")]

            # 2) 테이블 바디에서 모든 행 가져오기
            tbody_xpath = '//*[@id="wrapper"]/main/section[2]/div/div[2]/div[2]/table/tbody'
            tbody = driver.find_element(By.XPATH, tbody_xpath)

            rows_data = []
            row_index = 1

            while True:
                try:
                    # 각 행 XPath (인덱스 1부터 시작)
                    row_xpath = f'//*[@id="wrapper"]/main/section[2]/div/div[2]/div[2]/table/tbody/tr[{row_index}]'
                    row = driver.find_element(By.XPATH, row_xpath)
                    cells = row.find_elements(By.TAG_NAME, "td")
                    row_values = [cell.text.strip() for cell in cells]
                    rows_data.append(row_values)
                    row_index += 1
                except Exception as e:
                    # 더 이상 행이 없으면 종료
                    break

            # 3) pandas DataFrame 생성
            df = pd.DataFrame(rows_data, columns=headers)

            # 4) 엑셀 저장 (파일명에 선박명과 날짜 포함)
            filename = f"{self.download_dir}/{vessel_name.replace(' ', '_')}_{today}.xlsx"
            df.to_excel(filename, index=False)
            print(f"엑셀 저장 완료: {filename}")

        self.Close()