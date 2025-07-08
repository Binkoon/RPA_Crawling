# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/30 (완성)
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
        # 하위폴더명 = py파일명(소문자)
        self.subfolder_name = self.__class__.__name__.replace("_crawling", "").lower()
        self.download_dir = os.path.join(self.base_download_dir, self.subfolder_name)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        # 크롬 옵션에 하위폴더 지정 (드라이버 새로 생성 필요)
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        self.set_user_agent(chrome_options)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        prefs = {"download.default_directory": self.download_dir}
        chrome_options.add_experimental_option("prefs", prefs)
        # 기존 드라이버 종료 및 새 드라이버로 교체
        self.driver.quit()
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def run(self):
        # 0. 선사 접근
        vessel_name_list = ["YM CREDENTIAL" , "YM COOPERATION" ,"YM INITIATIVE"]
        driver = self.driver
        wait = self.wait

        columns = ["Port" , "Terminal" , "ETA-Date" , "ETA-Status" , "ETB-Date" , "ETB-Status" , "ETD-Date" , "ETD-Status"]

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
                    # 실제 데이터 row만 추출 (td가 columns 수와 맞지 않으면 break)
                    if len(tds) < len(columns):
                        break
                    row = [td.text.strip() for td in tds[:len(columns)]]
                    data.append(row)
                    row_idx += 1
                except Exception:
                    break

            # DataFrame 생성 및 엑셀 저장
            df = pd.DataFrame(data, columns=columns)
            save_path = os.path.join(self.download_dir, f'{vessel_name}_schedule.xlsx')
            df.to_excel(save_path, index=False)
            print(f"[{vessel_name}] 엑셀 저장 완료: {save_path}")
            time.sleep(1)

        self.Close()


# //*[@id="ContentPlaceHolder1_gvLast"]/tbody/tr[1]  - 크리덴셜
# //*[@id="ContentPlaceHolder1_gvLast"]/tbody/tr[1]  - 코퍼레이션