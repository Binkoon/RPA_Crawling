# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/07/01 (완성)
# 선사 링크 : https://asiaschedule.unifeeder.com/Softship.Schedule/default.aspx
# 선박 리스트 : ["NAVIOS BAHAMAS"]

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import os
import time
import pandas as pd
from .base import ParentsClass

class FDT_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "FDT"

    def run(self):
        # 0. 선사 접속
        self.Visit_Link("https://asiaschedule.unifeeder.com/Softship.Schedule/default.aspx")
        driver = self.driver
        wait = self.wait
        time.sleep(2)  # 충분히 쉬어줘야 함

        # 1. vessel 탭 클릭
        vessel_tab = wait.until(EC.element_to_be_clickable((By.ID, "searchByVesselTabHeader")))
        driver.execute_script("arguments[0].click();", vessel_tab)
        time.sleep(1)

        vessel_name_list = ["NAVIOS BAHAMAS"]
        for vessel_name in vessel_name_list:
            # 입력창 찾기
            input_box = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id="searchByVesselTab"]/div[1]/div[1]/div[2]//input'
            )))
            # 입력 초기화 및 입력 실행
            driver.execute_script("arguments[0].value = '';", input_box)
            driver.execute_script("arguments[0].focus();", input_box)
            time.sleep(0.2)
            input_box.send_keys(vessel_name)
            print(f"[{vessel_name}] 입력 완료")
            time.sleep(2)

            # 자동완성 클릭
            auto_item = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="BAHAMAS-"]')))
            auto_item.click()
            print(f"[{vessel_name}] 자동완성 선택 완료")
            time.sleep(1)

            # 검색 버튼 클릭
            search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_searchByVesselButton"]')))
            driver.execute_script("arguments[0].click();", search_btn)
            time.sleep(1.5)

            # 2. voyage_ports 클래스가 포함된 모든 table 가져오기
            tables = driver.find_elements(By.CSS_SELECTOR, "table.voyage_ports")
            # 3. voyage 클래스가 정확히 들어간 테이블도 따로 가져오기 새로 추가된 구문
            voy_tables = driver.find_elements(By.CSS_SELECTOR, "table.voyage")
            if not tables:
                print(f"[{vessel_name}] 테이블 없음 - 스킵")
                continue
            
            if len(tables) != len(voy_tables):
                print(f"[{vessel_name}] 테이블 수({len(tables)})와 Voyage 테이블 수({len(voy_tables)}) 불일치")
                continue

            all_data = []
            columns = ["Port", "Call ID", "Code", "ETA", "ETD" , "Voy"]

            for idx, table in enumerate(tables):
                # 동일한 인덱스의 voyage 테이블
                try:
                    voy_table = voy_tables[idx]
                    voyage_td = voy_table.find_element(By.XPATH, './/td[@id="VoyageNumber"]')
                    voyage_number = voyage_td.get_attribute("innerHTML").strip()
                except Exception as e:
                    print(f"[{vessel_name}] voyage_number 추출 실패 (index {idx}): {e}")
                    voyage_number = ""

                # 기존 데이터 row 추출 방식 유지 (홀수 row만)
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row_idx, tr in enumerate(rows):
                    if row_idx % 2 == 0:
                        continue  # 짝수 row는 skip
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 5:
                        continue
                    row = [td.text.strip() for td in tds[:5]]
                    row.append(voyage_number)  # 추가된 항차번호
                    all_data.append(row)

            # 4. DataFrame 저장
            if all_data:
                df = pd.DataFrame(all_data, columns=columns)
                save_path = self.get_save_path(self.carrier_name, vessel_name)
                df.to_excel(save_path, index=False)
                print(f"[{vessel_name}] 엑셀 저장 완료: {save_path}")
            else:
                print(f"[{vessel_name}] 추출된 데이터 없음 - 엑셀 저장 생략")

        self.Close()