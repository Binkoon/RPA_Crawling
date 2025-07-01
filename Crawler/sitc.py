# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/27
# 선사명 : SITC
# 선사링크 : https://ebusiness.sitcline.com/#/topMenu/vesselMovementSearch
# SITC에서 뽑아올 선박 리스트
"""
선박 리스트 : ["SITC DECHENG", "SITC BATANGAS" , "SITC SHENGMING" , "SITC QIMING",
                       "SITC XIN", "SITC YUNCHENG", "SITC MAKASSAR", "SITC CHANGDE", 
                       "SITC HANSHIN", "SITC XINGDE" ,"AMOUREUX"]
"""
############ 셀레니움 ###############
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
##############부모 클래스 ##############
from .base import ParentsClass
############# Schedule_Data쪽에 넘겨야함 ###########
import os
import pandas as pd

class SITC_Crawling(ParentsClass):
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
        # 0. 사이트 방문 들어가주고
        self.Visit_Link("https://ebusiness.sitcline.com/#/topMenu/vesselMovementSearch")
        driver = self.driver
        wait = self.wait  # 20초 대기

        # 입력창 (vesselSearch 내 el-input__inner 타겟팅, readonly 처리)
        vessel_input = wait.until(EC.presence_of_element_located((
            By.XPATH, '//*[@id="app"]/div[1]/div/section/div/div/div/form/div/div[1]/div/div/div/div/input'
        )))

        # readonly 속성 해제 및 활성화 시도
        driver.execute_script("arguments[0].removeAttribute('readonly');", vessel_input)
        vessel_input.click()  # focus 설정
        time.sleep(0.5)  # 활성화 대기

        # 1. 선박명 리스트 (테스트용으로 SITC DECHENG만)
        vessel_list = ["SITC DECHENG", "SITC BATANGAS" , "SITC SHENGMING" , "SITC QIMING",
                       "SITC XIN", "SITC YUNCHENG", "SITC MAKASSAR", "SITC CHANGDE", 
                       "SITC HANSHIN", "SITC XINGDE","AMOUREUX"]
        
        for vessel_name in vessel_list:
            vessel_input.clear()
            vessel_input.send_keys(vessel_name)
            print(f"입력: {vessel_name}")
            time.sleep(1)  # 드롭다운 뜨는 시간

            # 드롭다운 항목 클릭
            dropdown_xpath = "/html/body/div[2]/div[1]/div[1]/div/div[2]/div[2]/div"
            dropdown_item = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
            dropdown_item.click()
            print("드롭다운 항목 클릭")

            # Search 버튼 클릭
            search_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="app"]/div[1]/div/section/div/div/div/form/div/div[2]/button'
            )))
            search_button.click()
            print("Search 버튼 클릭")
            time.sleep(4)

            # 2. 데이터 테이블 추출
            tbody_xpath = '//*[@id="app"]/div[1]/div/section/div/div[2]/div[2]/div[3]/table/tbody'
            row_idx = 1
            data_rows = []
            while True:
                try:
                    row_xpath = f'{tbody_xpath}/tr[{row_idx}]'
                    row_elem = driver.find_element(By.XPATH, row_xpath)
                    cells = row_elem.find_elements(By.TAG_NAME, 'td')
                    row_data = [cell.text.strip() for cell in cells]
                    if row_data:
                        data_rows.append(row_data)
                    row_idx += 1
                except Exception:
                    break

            print(f"{vessel_name} 테이블 row 개수: {len(data_rows)}")

            # DataFrame으로 저장 및 엑셀로 내보내기
            if data_rows:
                df = pd.DataFrame(data_rows)
                save_path = os.path.join(self.download_dir, f"{vessel_name}_schedule.xlsx")
                df.to_excel(save_path, index=False, header=False)
                print(f"{vessel_name} 엑셀 저장 완료: {save_path}")
            else:
                print(f"{vessel_name} 데이터 없음")

        self.Close()

        # //*[@id="app"]/div[1]/div/section/div/div[2]/div[2]/div[3]/table/tbody
        # //*[@id="app"]/div[1]/div/section/div/div[2]/div[2]/div[3]/table/tbody/tr[1]