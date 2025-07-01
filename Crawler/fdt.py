# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/07/01
# 선사 링크 : https://asiaschedule.unifeeder.com/Softship.Schedule/default.aspx
# 선박 리스트 : ["NAVIOS BAHAMAS"]

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

import os,time
from .base import ParentsClass

class FDT_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()

    def run(self):
        # 0. 선사 접속
        self.Visit_Link("https://asiaschedule.unifeeder.com/Softship.Schedule/default.aspx")
        driver = self.driver
        wait = self.wait
        time.sleep(2) # 충분히 쉬어줘야함. 얘 많이 느림

        # 1. vessel 탭 클릭 
        vessel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="searchByVesselTabHeader"]'
        )))
        vessel_tab.click()
        
        # 2. dropdown 클릭
        vessel_select = wait.until(EC.element_to_be_clickable((
            By.XPATH ,'//*[@id="_menuPanel__tabControl_ctlf5c508ef_3f10_4e66_89b5_40d433ffe831__hostedControl__searchByVesselAutoCompleter__textBoxArrowDown"]'
        )))
        vessel_select.click()
        
        vessel_name_list = ["NAVIOS BAHAMAS"]
        for vessel_name in vessel_name_list:
            pass

        self.Close()
