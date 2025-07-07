# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/07/07 (완성)
# 선사 링크 : https://ebiz.pcsline.co.kr/
# 선박 리스트 : ["PEGASUS PETA","PEGASUS TERA","PEGASUS GLORY"]

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

import os,time
import pandas as pd

from .base import ParentsClass

class DYLINE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()

    def run(self):
        # 0. 선사 접속 링크
        self.Visit_Link("https://ebiz.pcsline.co.kr/")
        driver = self.driver
        wait = self.wait

        # 1. 스케줄 클릭 //*[@id="mf_wfm_header_gen_firstGenerator_0_btn_menu1_Label"]
        scheduel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="mf_wfm_header_gen_firstGenerator_0_btn_menu1_Label"]'
        )))
        scheduel_tab.click() # 만약 못알아먹으면 JS로 바꿔서 ㄱ
        time.sleep(0.5)

        # 2. 선박별 클릭  //*[@id="mf_wfm_header_grp_ul"]/li[1]/dl/dd[2]/a
        vessel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="mf_wfm_header_grp_ul"]/li[1]/dl/dd[2]/a'
        )))
        vessel_tab.click()
        time.sleep(0.5)

        # 3. 선박명 INPUT 클릭 //*[@id="mf_tac_layout_contents_00010004_body_ibx_vsl_input"]
        vessel_name_list = ["PEGASUS PETA"]
        for vessel_name in vessel_name_list:
            vessel_input = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_ibx_vsl_input"]'
            )))
            # 얘 그냥 셀레니움 click, send_keys로는 안됌. 이런 경우는 js로 ㄱㄱ
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

            # 조회 버튼
            search_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="mf_tac_layout_contents_00010004_body_btn_inq"]'
            )))
            search_btn.click()
            time.sleep(1)

        self.Close()