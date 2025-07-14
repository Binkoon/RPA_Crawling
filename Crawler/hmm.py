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

            # 4. 다운로드 클릭
            download_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="tab3Contents"]/div/div[3]/div[2]/button'
            )))
            download_btn.click()
            time.sleep(2) # 이거 무조건 넣어주셈. 안넣으면 아직 다운로드 중일때 프로세스 종료해서 .tmp 파일로 뱉게 된다.
        
        self.Close()


        vessel_name = "HMM BANGKOK"
        old_path = os.path.join(self.today_download_dir, "byVesselName.xls")
        new_path = os.path.join(self.today_download_dir, f"HMM_{vessel_name}.xls")
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"파일명 변경 완료: {new_path}")
        else:
            print("다운로드 파일이 없습니다.")

        if os.path.exists(new_path):
            df = pd.read_excel(new_path)
            col_map = {
                'Vessel Voyage No.': 'Vessel Code',
                'Arrival': 'ETA',
                'Berthing': 'ETB',
                'Departure': 'ETD'
            }
            df.rename(columns=col_map, inplace=True)
            df.to_excel(new_path, index=False)
            print(f"칼럼명 변경 및 저장 완료: {os.path.basename(new_path)}")

