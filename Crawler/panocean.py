# 선사 링크 : https://container.panocean.com/
# 선박 리스트 : 
"""
["POS SINGAPORE" , "POS YOKOHAMA" , "POS QINGDAO" , "POS GUANGZHOU",
 "POS HOCHIMINH", , "POS LAEMCHABANG"]
"""

################# User-agent 모듈 ###############
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
############### 셀레니움 기본 + time #####
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
######## 부모클래스
from .base import ParentsClass

class PANOCEAN_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()

    def run(self):
        # 0. 선사 홈페이지 접속
        self.Visit_Link("https://container.panocean.com/")
        driver = self.driver
        wait = self.wait

        time.sleep(4)
        # 1. 스케줄 탭 클릭
        schedule_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_btn_11000"]')))
        schedule_tab.click()
        time.sleep(1)

        # 2. 선박명 클릭 (iframe 내에서)
        vessel_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_btn_11002"]')))
        vessel_tab.click()
        time.sleep(1)

        self.Close()