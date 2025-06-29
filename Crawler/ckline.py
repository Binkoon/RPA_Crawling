# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/06/29
# 선사링크 (천경해운): https://es.ckline.co.kr/
# 선박 리스트 : ["SKY MOON" , "SKY FLOWER" , "SKY VICTORIA"]
# 추가 정보 : 로딩 화면이 존재함. wait 사용해서 화면 로딩시간 기다려줘야함.

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from .base import ParentsClass

import time

class CKLINE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()

    def run(self):
        # 0. 선사 방문
        self.Visit_Link("https://es.ckline.co.kr/")
        driver = self.driver
        wait = self.wait

        # 1. 오버레이가 안 보일 때까지 기다림 (ckline은 로딩화면이 존재함)
        wait.until(
            EC.invisibility_of_element_located((By.ID, "mf_grp_loading"))
        )

        # 2. 팝업 닫기
        pop_up_close = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="mf_btn_noti"]'
        )))
        pop_up_close.click()
        
        # 3. 1차 메뉴 클릭 (li[1])
        menu1 = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div/ul/li[1]')))
        menu1.click()

        # 4. (필수) 하위 메뉴가 펼쳐질 때까지 잠깐 대기
        time.sleep(0.5)  # 또는 WebDriverWait으로 하위 메뉴가 보일 때까지 대기

        # 5. 2차 메뉴 클릭 (li[1]/ul/li[2])
        submenu = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div/ul/li[1]/ul/li[2]')))
        submenu.click()

        print("메뉴 클릭 완료!")

        # 실제 입력창이 활성화된 input 태그를 찾아서 send_keys
        vessel_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel"]'))
        )
        
        vessel_name_list = ["SKY MOON"]
        for vessel_name in vessel_name_list:
            vessel_input.clear()
            vessel_input.send_keys(vessel_name)  # vessel_name은 반복문에서 사용

            # 자동완성 리스트 대기 (li 태그, 혹은 해당 리스트의 첫 번째 항목)
            auto_list_item = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"w2autocomplete_list") and contains(@style,"display: block")]/ul/li[1]'))
            )
            auto_list_item.click()

            search_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_btn_inquiry"]'))
            )
            search_button.click()
            time.sleep(1)

        self.Close()

