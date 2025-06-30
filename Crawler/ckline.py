# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/30
# 선사 링크 : https://es.ckline.co.kr/
# 선박 리스트 : ["SKY MOON" , "SKY FLOWER"]

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from .base import ParentsClass
import time

class CKLINE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()

    def run(self):
        # 0. 웹사이트 방문
        self.Visit_Link("https://es.ckline.co.kr/")
        driver = self.driver
        wait = self.wait

        # 1. 로딩 화면 대기
        wait.until(EC.invisibility_of_element_located((By.ID, "mf_grp_loading")))

        # 2. 팝업 닫기
        pop_up_close = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_btn_noti"]')))
        pop_up_close.click()

        # 3. 스케줄 메뉴 클릭
        menu1 = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div/ul/li[1]')))
        menu1.click()
        time.sleep(0.5)  # 하위 메뉴 표시 대기

        # 4. 선박 메뉴 클릭
        submenu = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div/ul/li[1]/ul/li[2]')))
        submenu.click()
        print("메뉴 클릭 완료!")
        time.sleep(1)  # 페이지 로드 대기 시간 증가

        # 5. 선박별 드롭다운 처리 - 다양한 방법으로 시도
        vessel_name_list = ["SKY MOON"]
        
        vessel_input = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_input"]'
        ))) # //*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_itemTable"]
        vessel_input.click()

        for vessel_name in vessel_name_list:
            vessel_input.clear()
            vessel_input.send_keys(vessel_name)
            # 리스트 클릭해야함.  //*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_itemTable_0"]
            # 드롭다운 리스트에서 첫 번째 항목 선택
            dropdown_item = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_itemTable_0"]'
            )))
            dropdown_item.click()
            print(f"선박 '{vessel_name}' 선택 완료!")

            # 조회 버튼 클릭
            inquiry_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_btn_inquiry"]'
            )))
            driver.execute_script("arguments[0].click();", inquiry_btn)
            print("조회 버튼 클릭 완료!")
            time.sleep(1)  # 조회 후 페이지 로드 대기
        
        self.Close()