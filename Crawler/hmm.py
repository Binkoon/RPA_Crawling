# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/07/01 (완성)
# 선사 링크 : https://www.hmm21.com/e-service/general/schedule/ScheduleMain.do
# 선박 리스트 : ["HMM BANGKOK"]

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from .base import ParentsClass
import os
import time
import pandas as pd

class HMM_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "HMM"

    def run(self):
        # 0. 선사 홈페이지 접속
        self.Visit_Link("https://www.hmm21.com/e-service/general/schedule/ScheduleMain.do")
        driver = self.driver
        wait = self.wait

        # 1. by vessel name 클릭  
        vessel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '/html/body/div[5]/div[3]/div[2]/div/div/ul/li[3]/a/div'
        )))
        vessel_tab.click()
        time.sleep(0.5)

        # 2. Vessel name 입력 //*[@id="srchByVesselVslCd"]
        vessel_name_list = ["HMM BANGKOK"]
        for vessel_name in vessel_name_list:
            select_elem = wait.until(EC.presence_of_element_located((
                By.ID , 'srchByVesselVslCd'
            )))
            select_item = Select(select_elem)

            found = False
            for option in select_item.options:
                if vessel_name in option.text:
                    select_item.select_by_visible_text(option.text)
                    print(f"선택함 : {option.text}")
                    found = True
                    break

            if not found:
                print("없는 선박임")
                continue
        
            
            time.sleep(1)

            # 3. 조회 버튼 클릭 
            search_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="tabItem03"]/div/div/div[1]/div[2]/div[3]/div/div[2]/div/button'
            )))
            search_btn.click()
            time.sleep(1.2) # 리스트 기다려줘

        # columns = ["Vessel Cdoe","Voyage" ,"Port","Terminal", "Rating Date", "ETA","ETB","ETD","Current Location"]
        # //*[@id="byVesselNameArea"]/tr[1] ~  //*[@id="byVesselNameArea"]/tr[8]
        # //*[@id="byVesselNextArea"]/div/div/a[2]  (next버튼)
        # //*[@id="byVesselNameArea"]/tr[1] ~  //*[@id="byVesselNameArea"]/tr[8]
        # -------------- 테이블 긁기: 페이지 1 --------------
            all_rows = []
            table_xpath_base = '//*[@id="byVesselNameArea"]/tr['

            def extract_table_rows():
                for idx in range(1, 9):  # tr[1]~tr[8]
                    try:
                        row_xpath = table_xpath_base + f"{idx}]"
                        tr = driver.find_element(By.XPATH, row_xpath)
                        tds = tr.find_elements(By.TAG_NAME, 'td')
                        row_data = [td.text.strip() for td in tds]
                        # 필터링 조건 추가 가능
                        if any(row_data):  # 빈 행 제거
                            all_rows.append(row_data)
                    except:
                        pass  # 혹시 없는 tr 인덱스는 건너뜀

            extract_table_rows()

            # -------------- 페이지 아래로 내리고 next 클릭 --------------
            driver.execute_script("window.scrollBy(0,150);")
            time.sleep(1)

            try:
                next_btn = driver.find_element(By.XPATH, '//*[@id="byVesselNextArea"]/div/div/a[2]')
                next_btn.click()
                time.sleep(1.5)  # 다음 페이지 로딩 대기
                extract_table_rows()  # 다음 페이지 8줄 추가로 긁기
            except Exception as e:
                print(f"다음 페이지 버튼 클릭 실패: {e}")

            # ----------- 엑셀 파일 저장 -----------
            columns = ["Vessel Code", "Voyage" ,"Port","Terminal", "Rating Date", "ETA","ETB","ETD","Current Location"]
            df = pd.DataFrame(all_rows, columns=columns)

            file_path = self.get_save_path(self.carrier_name, vessel_name, ext="xlsx")
            df.to_excel(file_path, index=False, engine="openpyxl")
            print(f"엑셀 저장 완료: {file_path}")

        self.Close()