# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/07/01 (완성)
# 선사 링크 : https://asiaschedule.unifeeder.com/Softship.Schedule/default.aspx
# 선박 리스트 : ["NAVIOS BAHAMAS"]

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import os, time
from .base import ParentsClass

import pandas as pd

class FDT_Crawling(ParentsClass):
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
        # 0. 선사 접속
        self.Visit_Link("https://asiaschedule.unifeeder.com/Softship.Schedule/default.aspx")
        driver = self.driver
        wait = self.wait
        time.sleep(2)  # 충분히 쉬어줘야함. 얘 많이 느림

        # 1. vessel 탭 클릭
        vessel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//*[@id="searchByVesselTabHeader"]'
        )))
        # JS로 클릭
        driver.execute_script("arguments[0].click();", vessel_tab)
        time.sleep(1)

        vessel_name_list = ["NAVIOS BAHAMAS"]  # //*[@id="BAHAMAS-"]
        for vessel_name in vessel_name_list:
            # input 박스 요소 찾기
            input_box = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id="searchByVesselTab"]/div[1]/div[1]/div[2]//input'
            )))
            # 값 비우기(JS)
            driver.execute_script("arguments[0].value = '';", input_box)
            # 포커스(JS)
            driver.execute_script("arguments[0].focus();", input_box)
            time.sleep(0.2)
            # send_keys로 실제 입력 (자동완성 리스트가 뜸)
            input_box.send_keys(vessel_name)
            print(f"입력: {vessel_name}")
            time.sleep(2)  # 자동완성 리스트 뜨는 시간 대기

            # 자동완성 리스트에서 원하는 항목 클릭
            auto_item = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="BAHAMAS-"]')))
            # driver.execute_script("arguments[0].click();", auto_item)
            auto_item.click()
            print("자동완성 리스트에서 BAHAMAS- 선택")
            time.sleep(1)

            # 검색 버튼 클릭(JS)
            search_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="_searchByVesselButton"]'
            )))
            driver.execute_script("arguments[0].click();", search_btn)
            time.sleep(1)

             # 2. 테이블 데이터 크롤링
            columns = ["Port", "Call ID", "Code", "ETA", "ETD"]
            data = []

            # 얘는 테이블 관련 xpath 따올때, 적힌 id명.
            table_id = "ports_256966"

            row_idx = 1
            while True:
                xpath = f'//*[@id="{table_id}"]/tbody/tr[{row_idx}]'
                try:
                    tr = driver.find_element(By.XPATH, xpath)
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 5:
                        break  # 데이터 row가 아니면 종료
                    row = [td.text.strip() for td in tds[:5]]
                    data.append(row)
                    row_idx += 2  # 1,3,5,7... 홀수만 접근
                except Exception as e:
                    # print(f"더 이상 row 없음: {e}")
                    break

            # 데이터프레임으로 저장
            df = pd.DataFrame(data, columns=columns)

            # 엑셀로 저장
            save_path = os.path.join(self.download_dir, f'{vessel_name}_schedule.xlsx')
            df.to_excel(save_path, index=False)
            print(f"엑셀 저장 완료: {save_path}")

        self.Close()
