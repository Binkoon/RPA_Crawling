# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/30 (완성)
# 선사 링크 : http://eservice.sinotrans.co.kr/eService/es_schedule02.asp?tid=100&sid=2
# 선박 리스트 : ["AVIOS" , "REN JIAN 27"]
# 추가 정보 : AVIOS는 지금 안쓰는 선박인거 같음. Phase Out 되었는지 운항팀 확인 필요

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

# 얘는 크롬 안써요  엣지 씁니다 ######
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService

from .base import ParentsClass
import os,re
import time

import pandas as pd

import openpyxl # 얘는 xls로 박아줌.
import pyexcel

class SNL_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "SNL"

        # 기존 드라이버 종료
        self.driver.quit()

        # SNL만 해당함!!!!!!!!!!!!! base.py 에다가 등록하면 대참사임
        # 기존 크롬 드라이버 종료
        self.driver.quit()
        # Edge 옵션 설정
        edge_options = EdgeOptions()
        edge_options.add_argument("--window-size=1920,1080")
        self.set_user_agent(edge_options)  # base.py에 이 함수가 크롬/엣지 모두에 적용 가능해야 함
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        edge_options.use_chromium = True
        edge_options.add_experimental_option("prefs", {
            "download.default_directory": self.today_download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        })

        # Edge 드라이버로 교체
        from selenium.webdriver import Edge
        self.driver = Edge(options=edge_options)
        self.wait = WebDriverWait(self.driver, 20)

    def run(self):
        # 0. 선사 링크 접속
        self.Visit_Link("http://eservice.sinotrans.co.kr/eService/es_schedule02.asp?tid=100&sid=2")
        driver = self.driver
        wait = self.wait

        # 1. 드랍다운에서 선택해야함
        select_vessel = driver.find_element(By.XPATH , '//*[@id="vslvoy"]/select')
        select_vessel_name = Select(select_vessel)

        vessel_name_list = ["REN JIAN 27"]

        for vessel_name in vessel_name_list:
            found = False
            for option in select_vessel_name.options:
                # 옵션 텍스트에 vessel_name이 포함되어 있으면 선택
                if vessel_name in option.text:
                    select_vessel_name.select_by_visible_text(option.text)
                    print(f"선택된 옵션: {option.text}")
                    found = True
                    selected_option_text = option.text
                    break
            if not found:
                print(f"'{vessel_name}'을(를) 포함하는 옵션이 없습니다.")
            
            search_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="table12"]/tbody/tr[2]/td[3]/img'
            )))
            search_btn.click()
            time.sleep(1)

            table_xpath = '/html/body/table[4]/tbody/tr[1]/td/table/tbody/tr[3]/td/table[2]'
            table = driver.find_element(By.XPATH, table_xpath)
            rows = table.find_elements(By.TAG_NAME, 'tr')

            # th 역할을 하는 첫번째 tr (항상 존재, tr[1])
            header_tr = rows[0]
            header_cells = header_tr.find_elements(By.TAG_NAME, 'td')
            header = [cell.text.strip() for cell in header_cells]

            # 만약 데이터 구조가 고정/예측 가능하면 예시처럼 직접 줘도 됩니다:
            # header = ['국가', '지역', 'TERMINAL', '입항예정일시', '출항예정일시']

            data = []

            # 2번째 tr부터, 2씩 증가해서 끝까지(데이터 행만 추출)
            for idx in range(1, len(rows), 2):
                tr = rows[idx]
                tds = tr.find_elements(By.TAG_NAME, 'td')
                if not tds:
                    continue  # 빈 행, 혹은 구조적 결함 패스
                values = [td.text.strip() for td in tds]
                # 데이터값이 비어 있거나 너무 짧으면 중지
                if all([v == "" for v in values]):
                    continue
                data.append(values)

            # pandas DataFrame으로 엑셀 저장
            import pandas as pd

            df = pd.DataFrame(data, columns=header)
            formatted_name = selected_option_text  # or vessel_name (원하는 값 기준으로)
            save_path = self.get_save_path(self.carrier_name, formatted_name, ext='xlsx')
            df.to_excel(save_path, index=False, engine='openpyxl')
            print(f"파일 저장 완료: {save_path}")

        
        self.Close()

