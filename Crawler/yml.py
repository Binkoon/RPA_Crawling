# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/30 (완성) - 2025/07/14 (2차 점검 완료)
# 선사 링크 : https://e-solution.yangming.com/e-service/Vessel_Tracking/SearchByVessel.aspx
# 선박 리스트 : ["YM CREDENTIAL" , "YM COOPERATION" ,"YM INITIATIVE"]

# https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel=YM%20CREDENTIAL|YCDL&&func=current&&LocalSite=
# https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel=YM%20COOPERATION|YCPR&&func=current&&LocalSite=
# https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel=YM%20INITIATIVE|YINT&&func=current&&LocalSite=

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from .base import ParentsClass
import os,time
from datetime import datetime

import pandas as pd

class YML_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "YML"  # 선사명 정확히!
        # self.columns는 필요시 사용

    def run(self):
        # 0. 선사 접속
        vessel_name_list = ["YM CREDENTIAL", "YM COOPERATION", "YM INITIATIVE"]
        driver = self.driver
        wait = self.wait

        columns = ["Port", "Terminal", "ETA-Date", "ETA-Status", "ETB-Date", "ETB-Status", "ETD-Date", "ETD-Status"]

        for vessel_name in vessel_name_list:
            vessel_name_param = vessel_name.replace(" ", "%20")
            vessel_code = {
                "YM CREDENTIAL": "YCDL",
                "YM COOPERATION": "YCPR",
                "YM INITIATIVE": "YINT"
            }[vessel_name]
            url = f'https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel={vessel_name_param}|{vessel_code}&&func=current&&LocalSite='
            self.Visit_Link(url)
            time.sleep(2)

            data = []
            row_idx = 1
            while True:
                xpath = f'//*[@id="ContentPlaceHolder1_gvLast"]/tbody/tr[{row_idx}]'
                try:
                    tr = driver.find_element(By.XPATH, xpath)
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) < len(columns):
                        break
                    row = [td.text.strip() for td in tds[:len(columns)]]
                    data.append(row)
                    row_idx += 1
                except Exception:
                    break

            df = pd.DataFrame(data, columns=columns)
            # === 오늘 날짜 폴더에 저장 ===
            save_path = self.get_save_path(self.carrier_name, vessel_name)
            df.to_excel(save_path, index=False, header=True)
            print(f"[{vessel_name}] 엑셀 저장 완료: {save_path}")
            time.sleep(1)

        self.Close()
