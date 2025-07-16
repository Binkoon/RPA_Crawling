# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/07/15 (완성)
# 선사 링크 : https://ebiz.pcsline.co.kr/
# 선박 리스트 : ["STARSHIP JUPITER, "STAR CHALLENGER" , "STAR PIONEER", "PEGASUS GRACE", "STAR FRONTIER", "STAR SKIPPER ,
# "STARSHIP MERCURY" , "STARSHIP TAURUS", "STARSHIP DRACO", "STARSHIP URSA", "STAR CLIPPER", "STAR EXPRESS", "STARSHIP AQUILA", "STAR CHASER",
# "STAR RANGER", "STARSHIP PEGASUS"]
# 추가 정보 : 스케줄 테이블 조회 시, 스크롤 액션 로직 넣어야함. EX) 실제 행은 10개있는데, <div class='table~~' ~~ > 이 clientHeight 값이 10개를 다 담지 못하고 있어서 눈에 보이는 row까지만 추출하고 멈춤.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

import os
import time
import pandas as pd

from .base import ParentsClass

class NSS_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "NSS"

    def run(self):
        # 0. 선사 접속 링크
        self.Visit_Link("https://ebiz.namsung.co.kr/")
        driver = self.driver
        wait = self.wait

        # 1. 스케줄 클릭
        scheduel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="mf_wfm_header_gen_firstGenerator_0_btn_menu1_Label"]'
        ))) # //*[@id="mf_wfm_header_gen_firstGenerator_0_btn_menu1_Label"]
        scheduel_tab.click()
        time.sleep(0.5)

        # 2. 선박별 클릭
        vessel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="mf_wfm_header_grp_ul"]/li[1]/dl/dd[2]/a'
        ))) # //*[@id="mf_wfm_header_grp_ul"]/li[1]/dl/dd[2]/a
        vessel_tab.click()
        time.sleep(0.5)

        # 3. 선박명 INPUT 클릭 및 처리
        vessel_name_list = ["STARSHIP JUPITER"]
        
        for vessel_name in vessel_name_list:
            all_rows = []
            vessel_input = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_ibx_vsl_input"]'
            ))) # //*[@id="mf_tac_layout_contents_00010004_body_ibx_vsl_input"]
            driver.execute_script("arguments[0].click();", vessel_input)
            driver.execute_script("arguments[0].value = '';", vessel_input)
            driver.execute_script(f"arguments[0].value = '{vessel_name}';", vessel_input)
            driver.execute_script(
                "var event = new Event('input', { bubbles: true }); arguments[0].dispatchEvent(event);",
                vessel_input
            )
            time.sleep(1)
            autocomplete_item = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_ibx_vsl_itemTable_0"]'
            )))
            driver.execute_script("arguments[0].click();", autocomplete_item)
            time.sleep(1)

            # 항차번호 드롭다운 반복
            index = 1
            while True:
                try:
                    # 드롭다운 버튼 클릭
                    voy_dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_ibx_voy_button"]')))
                    driver.execute_script("arguments[0].click();", voy_dropdown_btn)
                    time.sleep(0.5)

                    # 항차 tr 클릭
                    tr_xpath = f'//*[@id="mf_tac_layout_contents_00010004_body_ibx_voy_itemTable_main"]/tbody/tr[{index}]'
                    voyage_tr = wait.until(EC.element_to_be_clickable((By.XPATH, tr_xpath)))
                    voyage_tr.click()
                    time.sleep(0.5)

                    # 조회 버튼 클릭
                    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_btn_inq"]')))
                    search_btn.click()
                    time.sleep(1)

                except Exception:
                    print("oh shit")

        self.Close()
