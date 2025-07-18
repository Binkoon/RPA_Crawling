# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/07/07 (완성)
# 선사 링크 : https://ebiz.pcsline.co.kr/
# 선박 리스트 : ["PEGASUS PETA","PEGASUS TERA","PEGASUS GLORY"]
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

class DYLINE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "DYL"

    def run(self):
        # 0. 선사 접속 링크
        self.Visit_Link("https://ebiz.pcsline.co.kr/")
        driver = self.driver
        wait = self.wait

        # 1. 스케줄 클릭
        scheduel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="mf_wfm_header_gen_firstGenerator_0_btn_menu1_Label"]'
        )))
        scheduel_tab.click()
        time.sleep(0.5)

        # 2. 선박별 클릭
        vessel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="mf_wfm_header_grp_ul"]/li[1]/dl/dd[2]/a'
        )))
        vessel_tab.click()
        time.sleep(0.5)

        # 3. 선박명 INPUT 클릭 및 처리
        vessel_name_list = ["PEGASUS TERA","PEGASUS GLORY"] # ["PEGASUS PETA"]
        
        for vessel_name in vessel_name_list:
            all_rows = []
            vessel_input = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_ibx_vsl_input"]'
            )))
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

            index = 1
            while True:
                try:
                    voy_dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_ibx_voy_button"]')))
                    driver.execute_script("arguments[0].click();", voy_dropdown_btn)
                    time.sleep(0.5)

                    tr_xpath = f'//*[@id="mf_tac_layout_contents_00010004_body_ibx_voy_itemTable_main"]/tbody/tr[{index}]'
                    voyage_tr = wait.until(EC.element_to_be_clickable((By.XPATH, tr_xpath)))
                    voyage_text = voyage_tr.text.strip()
                    voyage_tr.click()
                    time.sleep(0.5)

                    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_btn_inq"]')))
                    search_btn.click()
                    time.sleep(1)

                    # 스크롤 없이 현재 보이는 tr만 추출
                    table_xpath = '//*[@id="mf_tac_layout_contents_00010004_body_grd_cur_body_table"]'
                    table_elem = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
                    tr_list = table_elem.find_elements(By.TAG_NAME, 'tr')
                    for tr in tr_list:
                        row_data = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, 'td')]
                        row_data.append(voyage_text)
                        all_rows.append(row_data)

                    index += 1
                except Exception:
                    break

            if all_rows:
                columns = ['No','Port','Skip','Terminal','ETA-Day','ETA-Date','ETA-Time','ETD-Day','ETD-Date','ETD-Time','Remark','Voy']
                df = pd.DataFrame(all_rows, columns=columns)
                save_path = self.get_save_path(self.carrier_name, vessel_name)
                df.to_excel(save_path, index=False)
                print(f"엑셀 저장 완료: {save_path}")

        self.Close()
