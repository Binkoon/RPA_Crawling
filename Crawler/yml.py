# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/30 (완성) - 2025/07/14 (디버깅 완료)
# 선사 링크 : https://e-solution.yangming.com/e-service/Vessel_Tracking/SearchByVessel.aspx
# 선박 리스트 : ["YM CREDENTIAL" , "YM COOPERATION" ,"YM INITIATIVE"]

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from .base import ParentsClass
import os,time
from datetime import datetime

import pandas as pd

# 쿠키 agree : /html/body/div/div/a
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

        columns = ["Port", "Terminal", "ETA", "ETA-Status", "ETB", "ETB-Status", "ETD", "ETD-Status", "Voy"]

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

            # 쿠키 팝업 있으면 클릭
            try:
                cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/a')))
                cookie_button.click()
                print("쿠키 팝업 클릭 완료")
            except Exception:
                pass

            # 항차번호 추출 //*[@id="ContentPlaceHolder1_lblComn"]
            try:
                voyage_no_elem = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_lblComn"]'))
                )
                voyage_no = voyage_no_elem.text.strip()
            except Exception:
                voyage_no = ""
                print("항차번호 추출 실패")

            # 스크롤 Y 100px 내리기
            driver.execute_script("window.scrollBy(0, 100);")
            time.sleep(0.5)

            all_rows = []
            row_idx = 1
            while True:
                xpath = f'//*[@id="ContentPlaceHolder1_gvLast"]/tbody/tr[{row_idx}]'
                try:
                    tr = driver.find_element(By.XPATH, xpath)
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    row = [td.text.strip() for td in tds]  # TD 개수 제한 없이 전체 긁어오기
                    all_rows.append(row)
                    row_idx += 1
                except Exception:
                    break

            # 스크롤 Y 100px 올리기
            driver.execute_script("window.scrollBy(0, -100);")
            time.sleep(0.5)

            # 다음 버튼 클릭
            try:
                next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_btnNext"]')))
                next_btn.click()
                time.sleep(1.5)
            except Exception:
                print("다음 페이지 버튼 없음 또는 클릭 실패")

            # 두 번째 페이지 데이터도 추가로 긁어서 같은 리스트에 저장
            row_idx = 1
            while True:
                xpath = f'//*[@id="ContentPlaceHolder1_gvLast"]/tbody/tr[{row_idx}]'
                try:
                    tr = driver.find_element(By.XPATH, xpath)
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    row = [td.text.strip() for td in tds]
                    all_rows.append(row)
                    row_idx += 1
                except Exception:
                    break

            # DataFrame으로 저장 (columns 없이 저장)
            df = pd.DataFrame(all_rows)

            # Port/Terminal/ETA/ETA-Status/ETB/ETB-Status/ETD/ETD-Status 열만 남기고, Voy 칼럼 오른쪽에 추가
            try:
                df.drop(columns=[0, 2], inplace=True)
            except Exception:
                print("DataFrame drop 실패 - 인덱스를 확인하세요.")
            df.columns = columns[:-1]
            df["Voy"] = voyage_no  # 맨 오른쪽 Voy 칼럼

            save_path = self.get_save_path(self.carrier_name, vessel_name)
            df.to_excel(save_path, index=False, header=True)
            print(f"[{vessel_name}] 테이블 원본 저장 완료: {save_path}")
            time.sleep(1)

        self.Close()
