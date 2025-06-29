# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/28
# 선사 링크 : https://www.one-line.com/en
# 선박 리스트 : ["ONE REASSURANCE" , "SAN FRANCISCO BRIDGE"]

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base import ParentsClass
import time

class ONE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()

    def run(self):
        # 0. 선사 접속 & iframe 확인
        self.Visit_Link("https://www.one-line.com/en")
        driver = self.driver
        wait = self.wait        
        # 페이지가 완전히 로드될 때까지 기다리기
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        
        # iframe이 있는지 확인하고 전환
        try:
            iframe = driver.find_element(By.TAG_NAME, "iframe")
            driver.switch_to.frame(iframe)
            print("iframe으로 전환됨")
        except:
            print("iframe 없음, 메인 페이지에서 진행")
        
        # 1. Vessel Tab 확인
        vessel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="__next"]/div/div/div/div[3]'
        )))
        vessel_tab.click()
        
        vessel_input = wait.until(EC.presence_of_element_located((
            By.XPATH , '//*[@id="vessel-input"]'
        )))
        
        # 2. 선박 리스트 넣기
        vessel_name_list = ["ONE REASSURANCE"]
        for vessel_name in vessel_name_list:
            vessel_input.clear()
            vessel_input.send_keys(vessel_name)
            time.sleep(0.5)

            dropdown_menu = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id="vessel-menu"]'
            )))
            print("✅ 드롭다운 메뉴 확인됨")
            
            # 2-3. 드롭다운에서 정확한 선박 선택
            # 방법 1: 첫 번째 옵션 선택
            first_option = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="vessel-menu"]//li[1]'  # 첫 번째 항목
            )))
            first_option.click()

            search_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH , '/html/body/div[1]/div/div/form[2]/div/div[2]/div/button[2]'
            )))
            # search_btn.click()
            # click 메서드가 안먹을 때는 JS로 직접 찔러주기.  ElementClickInterceptedException  <- 이 에러는 어떤 요소에 의해 가려져서 발생
            # 
            driver.execute_script("arguments[0].click();", search_btn)
            time.sleep(1)

            download_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="__next"]/main/div[2]/div[2]/div[7]/div[1]/div[3]/div/div[2]/button'
            )))
            driver.execute_script("arguments[0].click();", download_btn)

        
        # time.sleep(2)
        self.Close()