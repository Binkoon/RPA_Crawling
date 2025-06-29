# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/28
# 선사 링크 : https://www.one-line.com/en
# 선박 리스트 : ["ONE REASSURANCE (RSCT)" , "SAN FRANCISCO BRIDGE"]

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base import ParentsClass

class ONE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()

    def run(self):
        # 0. 선사 링크 접속 할거임
        self.Visit_Link("https://www.one-line.com/en")
        driver = self.driver
        wait = self.wait

        # Vessel 탭 클릭
        vessel_name_tab = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/div/div/div[3]'))
        )
        vessel_name_tab.click()
        
        # self.Close()
        vessel_name_input = wait.until(EC.presence_of_element_located((
            By.XPATH , '//*[@id="vessel-input"]'
        )))

        # 2. vessel name 입력
        vessel_name_list = ["ONE REASSURANCE (RSCT)"]
        for vessel_name in vessel_name_list:
            vessel_name_input.clear()
            vessel_name_input.click()
            vessel_name_input.send_keys(vessel_name)

            dropdown_item = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="vessel-menu"]'
            )))
            dropdown_item.click()

            # Search 버튼 클릭
            search_button = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="schedule-box-search-btn-id"]'
            )))
            search_button.click()


        self.Close()