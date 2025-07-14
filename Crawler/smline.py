# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/06/30 (완성)
# 선사 링크 : https://esvc.smlines.com/smline/CUP_HOM_3005.do?sessLocale=ko
# 선박 리스트 : ["SM JAKARTA"]
# 추가 정보 : 다운로드가 바로 되지 않고, "다른 이름으로 저장"으로 뜨는 경우는 아래 코드 사용.
# ++ 셀레니움의 Options를 사용할 것. 예시 코드는 아래에 있음. def __init__ 에 넣고 절대경로로 해야함.
"""
download_folder = r"C:\원하는\폴더\경로"  # 원하는 다운로드 경로로 변경

chrome_options = Options()
prefs = {
    "download.default_directory": download_folder,  # 다운로드 폴더 지정
    "download.prompt_for_download": False,          # 저장 위치 묻기 비활성화
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from .base import ParentsClass
import time
import os

class SMLINE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "SM LINE"

        # SMLINE은 저장할때, "다름이름으로 저장이 떠가지고 얘만 따로"
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        self.set_user_agent(chrome_options)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        prefs = {"download.default_directory": self.today_download_dir}
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver.quit()
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def run(self):
        # 0. 선사 접속
        self.Visit_Link("https://esvc.smlines.com/smline/CUP_HOM_3005.do?sessLocale=ko")
        driver = self.driver
        wait = self.wait

        # 1. input 찾기
        vessel_input = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="vslEngNm"]'
        )))
        vessel_input.click()

        vessel_name_list = ["SM JAKARTA"]
        # 2. 선박 넣기
        for vessel_name in vessel_name_list:
            vessel_input.clear()
            vessel_input.send_keys(vessel_name)
            time.sleep(1)

            vessel_select = wait.until(EC.element_to_be_clickable((
                By.XPATH , '/html/body/ul/li'
            )))
            vessel_select.click()
            time.sleep(1)

            search_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="btnSearch"]'
            )))
            search_btn.click()
            time.sleep(1)

            download_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="btnDownload"]'
            )))
            download_btn.click()
            time.sleep(1)

            for f in os.listdir(self.today_download_dir):
                if vessel_name.replace(" ", "") in f.replace(" ", ""):
                    # 예:"SM LINE_SM JAKARTA.xlsx"
                    old_path = os.path.join(self.today_download_dir, f)
                    new_name = f"{self.carrier_name}_{vessel_name}.xlsx"
                    new_path = os.path.join(self.today_download_dir, new_name)
                    os.rename(old_path, new_path)
                    print(f"파일명 변경 완료: {new_path}")
                    break
        
        self.Close()
