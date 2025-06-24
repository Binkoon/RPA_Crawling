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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import ParentsClass
import time

class SITC_Crawling(ParentsClass):
    def run(self):  # 사이트 방문 들어가주고
        self.Visit_Link("https://ebusiness.sitcline.com/#/home")
        driver = self.driver
        wait = self.wait  # 20초 대기

        # Vessel Movement 탭 클릭 (요청에 따라 유지)
        vessel_movement_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[contains(@class, 'border-card') and contains(text(), 'Vessel Movement')]"
        )))
        vessel_movement_tab.click()
        time.sleep(1)  # 탭 전환 대기

        # 입력창 (vesselSearch 내 el-input__inner 타겟팅, readonly 처리)
        vessel_input = wait.until(EC.presence_of_element_located((
            By.XPATH, "//div[contains(@class, 'vesselsSearch')]//input[@type='text' and contains(@class, 'el-input__inner')]"
        )))

        # readonly 속성 해제 및 활성화 시도
        driver.execute_script("arguments[0].removeAttribute('readonly');", vessel_input)
        vessel_input.click()  # focus 설정
        time.sleep(0.5)  # 활성화 대기

        # 선박명 리스트 (테스트용으로 SITC DECHENG만)
        vessel_list = ["SITC DECHENG"]
        
        for vessel_name in vessel_list:
            vessel_input.clear()
            vessel_input.send_keys(vessel_name)
            print(f"입력: {vessel_name}")  # 디버깅 로그
            time.sleep(1)  # 드롭다운 열릴 시간 대기

            # 드롭다운 목록 선택 (contains로 유연화)
            try:
                # 드롭다운 컨테이너 대기
                wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'el-select-dropdown')]")))
                dropdown_item = wait.until(EC.element_to_be_clickable((
                    By.XPATH, f"//div[contains(@class, 'el-select-dropdown')]//span[contains(text(), '{vessel_name}')]"
                )))
                dropdown_item.click()
                print(f"드롭다운 선택 성공: {vessel_name}")
            except Exception as e:
                print(f"드롭다운에서 '{vessel_name}'을 찾을 수 없습니다. 오류: {str(e)}. 키보드 입력으로 시도합니다.")
                vessel_input.send_keys(Keys.DOWN)
                vessel_input.send_keys(Keys.ENTER)
                print("키보드 입력으로 대체 시도")

            # Search 버튼 클릭
            search_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//div[contains(@class, 'vesselsSearch')]//button[contains(@class, 'el-button--primary') and contains(text(), 'Search')]"
            )))
            search_button.click()
            print("Search 버튼 클릭")

            # 검색 후 대기
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)  # 결과 로드 대기
            print("검색 완료 대기")

        self.Close()