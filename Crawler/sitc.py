# 선사명 : SITC
# 선사링크 : https://ebusiness.sitcline.com/#/home
# SITC에서 뽑아올 선박 리스트
"""
["SITC DECHENG", "SITC BATANGAS" , "SITC SHENGMING" , "SITC QIMING",
                       "SITC XIN", "SITC YUNCHENG", "SITC MAKASSAR", "SITC CHANGDE", 
                       "SITC HANSHIN", "SITC XINGDE"]
"""
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # 명시적 대기용
from selenium.webdriver.support import expected_conditions as EC
########### 아래는 자식클래스 (선사) 들 import 목록 ############
from .base import ParentsClass

class SITC_Crawling(ParentsClass):
    def run(self): # 사이트 방문 들어가주고
        self.Visit_Link("https://ebusiness.sitcline.com/#/home")
        driver = self.driver
        wait = self.wait # 10초 대기

        # 여기는 Vessel tab 클릭
        vessel_movement_tab = wait.until(EC.element_to_be_clickable( (
            By.XPATH, "//div[contains(@class, 'border-card') and contains(text(), 'Vessel Movement')]"
        )))
        vessel_movement_tab.click()

        # 여기는 해당 탭의 입력창
        vessel_input = wait.until(EC.element_to_be_clickable( (
            By.XPATH, "//input[contains(@class, 'el-input') and contains(@class, 'el-input--mini') and contains(@class, 'el-input--suffix')]"
        )))

        # 선박명은 풀네임으로 받아오자. 선박코드는 ICC - Vessel information에서 매핑작업 치면 된다.
        vessel_list = ["SITC DECHENG"]
        
        for vessel_name in vessel_list:
            vessel_input.clear()
            vessel_input.send_keys(vessel_name)

            # dropdown 리스트 뜨는거
            dropdown_item_list = wait.until(EC.element_to_be_clickable((
                By.XPATH, f"//div[contains(@class, 'gl-associate-tbody')]//span[contains(@class, 'gl-associate-td') and text()='{vessel_name}']"
            )))
            dropdown_item_list.click()

            # Search 버튼 클릭
            search_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//button[contains(@class, 'el-button--primary') and text()='Search']"
            )))
            search_button.click()

        self.Close()


"""

"""