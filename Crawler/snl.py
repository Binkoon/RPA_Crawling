# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/30 (완성)
# 선사 링크 : http://eservice.sinotrans.co.kr/eService/es_schedule02.asp?tid=100&sid=2
# 선박 리스트 : ["AVIOS" , "REN JIAN 27"]
# 추가 정보 : AVIOS는 지금 안쓰는 선박인거 같음. Phase Out 되었는지 운항팀 확인 필요

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from .base import ParentsClass
import os
import time

class SNL_Crawling(ParentsClass):
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
        # 0. 선사 링크 접속
        self.Visit_Link("http://eservice.sinotrans.co.kr/eService/es_schedule02.asp?tid=100&sid=2")
        driver = self.driver
        wait = self.wait

        # 1. 드랍다운에서 선택해야함
        select_vessel = driver.find_element(By.XPATH , '//*[@id="vslvoy"]/select')
        select_vessel_name = Select(select_vessel)

        vessel_name_list = ["REN JIAN 27"]

        for vessel_name in vessel_name_list:
            found = False
            for option in select_vessel_name.options:
                # 옵션 텍스트에 vessel_name이 포함되어 있으면 선택
                if vessel_name in option.text:
                    select_vessel_name.select_by_visible_text(option.text)
                    print(f"선택된 옵션: {option.text}")
                    found = True
                    break
            if not found:
                print(f"'{vessel_name}'을(를) 포함하는 옵션이 없습니다.")
            
            search_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="table12"]/tbody/tr[2]/td[3]/img'
            )))
            search_btn.click()
            time.sleep(1)

            # 2. 엑셀 다운로드 선택
            download_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="table2"]/tbody/tr/td[2]/p/span'
            )))
            print("다운로드 합니다.")
            download_btn.click()

        self.Close()
            