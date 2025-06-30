# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/26
# 선사링크 : https://ss.shipmentlink.com/tvs2/jsp/TVS2_VesselSchedule.jsp
# 선박 리스트 : ["EVER LUCID"]

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from .base import ParentsClass
import pandas as pd
import time

class EVERGREEN_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()

    def run(self):
        # 0. 선사 홈페이지 접속
        self.Visit_Link("https://ss.shipmentlink.com/tvs2/jsp/TVS2_VesselSchedule.jsp")
        driver = self.driver
        wait = self.wait

        vessel_name_list = ["EVER LUCID"]
        all_tables = []

        for vessel_name in vessel_name_list:
            vessel_select_elem = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="vslCode"]'))
            )
            vessel_select = Select(vessel_select_elem)

            for option in vessel_select.options:
                if vessel_name in option.text:
                    vessel_select.select_by_visible_text(option.text)
                    print(f"선박명 '{vessel_name}' 선택 완료")
                    break

            time.sleep(1)

            submit_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="submitButton"]'))
            )
            submit_btn.click()
            print(f"Submit 버튼 클릭 완료")

            time.sleep(2)  # 데이터 로딩 대기

            tables = self.driver.find_elements(By.TAG_NAME, 'table')

            for table in tables:
                html = table.get_attribute('outerHTML')
                dfs = pd.read_html(html)  # 여러 개의 테이블이 있을 수 있음
                for df in dfs:
                    all_tables.append(df)

        # 엑셀로 저장
        with pd.ExcelWriter('evergreen_schedule.xlsx') as writer:
            for idx, df in enumerate(all_tables):
                df.to_excel(writer, sheet_name=f'Table_{idx+1}', index=False)

        self.Close()
        print("엑셀 저장 완료")
