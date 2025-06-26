# 선사명 : SITC
# 선사링크 : https://ebusiness.sitcline.com/#/home
# SITC에서 뽑아올 선박 리스트 /html/body/div[2]/div[1]/div[1]/div/div[2]/div[2]/div/span[2]
"""
["SITC DECHENG", "SITC BATANGAS" , "SITC SHENGMING" , "SITC QIMING",
                       "SITC XIN", "SITC YUNCHENG", "SITC MAKASSAR", "SITC CHANGDE", 
                       "SITC HANSHIN", "SITC XINGDE"]
"""
############ 셀레니움 ###############
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
##############부모 클래스 ##############
from .base import ParentsClass
############# Schedule_Data쪽에 넘겨야함 ###########
import os
import pandas as pd

class SITC_Crawling(ParentsClass):
    def run(self):  
        # 0. 사이트 방문 들어가주고
        self.Visit_Link("https://ebusiness.sitcline.com/#/home")
        driver = self.driver
        wait = self.wait  # 20초 대기

        # 1. Vessel Movement 탭 클릭
        vessel_movement_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[contains(@class, 'border-card') and contains(text(), 'Vessel Movement')]"
        )))
        vessel_movement_tab.click()
        time.sleep(1)  # 탭 전환 대기

        # 입력창 (vesselSearch 내 el-input__inner 타겟팅, readonly 처리)
        vessel_input = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[4]/div[3]/div/div[3]/div/input'
        )))

        # readonly 속성 해제 및 활성화 시도
        driver.execute_script("arguments[0].removeAttribute('readonly');", vessel_input)
        vessel_input.click()  # focus 설정
        time.sleep(0.5)  # 활성화 대기

        # 선박명 리스트 (테스트용으로 SITC DECHENG만)
        vessel_list = ["SITC DECHENG"]
        
        for vessel_name in vessel_list:
            vessel_input.clear()
            vessel_input.send_keys(vessel_name)
            print(f"입력: {vessel_name}")
            time.sleep(1)  # 드롭다운 뜨는 시간

            # 드롭다운 항목 클릭
            dropdown_xpath = "/html/body/div[2]/div[1]/div[1]/div/div[2]/div[2]/div/span[2]"
            dropdown_item = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
            dropdown_item.click()
            print("드롭다운 항목 클릭")

            # Search 버튼 클릭
            search_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[4]/div[3]/button'
            )))
            search_button.click()
            print("Search 버튼 클릭")

            # 스케줄 정보 헤더영역 찾기
            header_xpath = '//*[@id="app"]/div[1]/div/section/div/div[2]/div[2]/div[2]/table/thead/tr/th'
            headers = [th.text.strip() for th in driver.find_elements(By.XPATH, header_xpath)]

            # 스케줄 정보 row 추출
            row_xpath = '//*[@id="app"]/div[1]/div/section/div/div[2]/div[2]/div[2]/table/tbody/tr'
            rows = driver.find_elements(By.XPATH, row_xpath)
            data = []
            for tr in rows:
                cells = tr.find_elements(By.XPATH, './td')
                data.append([td.text.strip() for td in cells])

            # 엑셀로 저장
            df = pd.DataFrame(data, columns=headers)
            df.to_excel("sitc_sample_data.xlsx", index=False)

        self.Close()

        #//*[@id="app"]/div[1]/div/section/div/div[2]/div[2]/div[3]/table/tbody