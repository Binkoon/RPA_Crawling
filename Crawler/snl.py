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
                    break
            if not found:
                print(f"'{vessel_name}'을(를) 포함하는 옵션이 없습니다.")
            
            search_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="table12"]/tbody/tr[2]/td[3]/img'
            )))
            search_btn.click()
            time.sleep(1)

            # 2. 엑셀 다운로드 선택
            download_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="table2"]/tbody/tr/td[2]/p/span'
            )))
            print("다운로드 합니다.")
            download_btn.click()
            time.sleep(3)

        self.Close()
        
        old_path = os.path.join(self.today_download_dir, "sinotrans_schedule02.xls")
        new_path = os.path.join(self.today_download_dir, f"SNL_{vessel_name}.xlsx")
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"파일명 변경 완료: {new_path}")
        else:
            print("다운로드 파일이 없습니다.")