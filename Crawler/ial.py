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
        self.carrier_name = "IAL"

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

            header_map = {
                "Arrival":"ETA",
                "Berth":"ETB",
                "Departure":"ETD"
            }

            new_headers = []
            for h in headers:
                new_headers.append(header_map.get(h,h))
            
            new_headers = ["Vessel Name"] + new_headers

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
            
            row_data_with_vessel = [[vessel_name] + row for row in rows_data]

            # 3) pandas DataFrame 생성
            df = pd.DataFrame(row_data_with_vessel, columns=new_headers)
            # 4) 엑셀 저장 (파일명에 선박명과 날짜 포함)
            filename = self.get_save_path(self.carrier_name, vessel_name)
            df.to_excel(filename, index=False, header=True)
            print(f"엑셀 저장 완료: {filename}")

        self.Close()