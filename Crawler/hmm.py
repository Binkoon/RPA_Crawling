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

class HMM_Crawling(ParentsClass):
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


