# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/06/30 (완성)
# 선사 링크 : https://esvc.smlines.com/smline/CUP_HOM_3005.do?sessLocale=ko
# 선박 리스트 : ["SM JAKARTA"]
# 추가 정보 : 다운로드가 바로 되지 않고, "다른 이름으로 저장" 이 뜨는 선사임. 셀레니움의 Options를 사용할 것. 예시 코드는 아래에 있음. def __init__ 에 넣을 것.
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

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base import ParentsClass
import time

class SMLINE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()

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
        
        self.Close()
