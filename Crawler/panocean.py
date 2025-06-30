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

        # 1. 로딩 화면 대기
        #wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'wrap-loading')))

        # try:
        #     iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        #     driver.switch_to.frame(iframe)
        #     print("iframe으로 전환되었습니다.")
        # except Exception as e:
        #     print(f"iframe 찾기 실패, 메인 콘텐츠로 진행: {e}")
        time.sleep(4)
        # 2. 스케줄 탭 클릭
        schedule_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_btn_11000"]')))
        schedule_tab.click()
        driver.execute_script("arguments[0].click();", schedule_tab)

        # 4. 선박명 클릭 (iframe 내에서)
        vessel_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_btn_11002"]')))
        driver.execute_script("arguments[0].click();", vessel_tab)

        self.Close()