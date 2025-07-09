# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/26
# 선사링크 : https://ss.shipmentlink.com/tvs2/jsp/TVS2_VesselSchedule.jsp
# 선박 리스트 : ["EVER LUCID","EVER ELITE","EVER LASTING","EVER VIM"]
# 추가 정보 : 하나의 tr에  ARR , DEP이 같이 있음. 따라서 엑셀 전처리 작업이 추가로 필요함.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

from .base import ParentsClass
import pandas as pd
import time,os

class EVERGREEN_Crawling(ParentsClass):
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
            ############## 여기서부터 테이블 긁어오는 것. #############
            # 1. 페이지 내 모든 table 태그 찾기  
            # 이런 인덱스를 타고 있다.
            # # //*[@id="schedule"]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/table[1]/tbody/tr/td/table/tbody/tr[1]
            # //*[@id="schedule"]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/table[1]/tbody/tr/td/table/tbody/tr[2]
            #####################################
            # //*[@id="schedule"]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr[1]
            # //*[@id="schedule"]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr[2]
            # ====== 테이블 반복 추출 시작 ======
            table_idx = 1
            while True:
                try:
                    # 각 테이블의 1, 2번째 row만 추출
                    table_data = []
                    for row_idx in [1, 2]:
                        row_xpath = f'//*[@id="schedule"]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/table[{table_idx}]/tbody/tr/td/table/tbody/tr[{row_idx}]'
                        row_elem = wait.until(
                            EC.presence_of_element_located((By.XPATH, row_xpath))
                        )
                        tds = row_elem.find_elements(By.TAG_NAME, "td")
                        row_data = [td.text.strip() for td in tds]
                        table_data.append(row_data)
                    all_tables.append(table_data)
                    table_idx += 1
                except Exception:
                    # 더 이상 table이 없으면 break
                    break

        # ====== 데이터 저장 ======
        # 테이블별로 DataFrame 변환 후 concat
        df_list = []
        for table in all_tables:
            if len(table) == 2:
                df = pd.DataFrame([table[1]], columns=table[0])
                df_list.append(df)
        if df_list:
            result_df = pd.concat(df_list, ignore_index=True)
            # 파일명에 선박명 포함
            filename = f"{vessel_name_list[0]}_schedule.xlsx"
            filepath = os.path.join(self.download_dir, filename)
            result_df.to_excel(filepath, index=False)
            print(f"엑셀 저장 완료: {filepath}")

            # =========================
            # 1. ARRDEP 전처리 추가
            # =========================
            processed_rows = []
            for idx, row in result_df.iterrows():
                for col in result_df.columns:
                    cell = row[col]
                    # ARRDEP 형식인지 체크
                    if isinstance(cell, str) and len(cell) == 9 and cell.count('/') == 2:
                        arr = cell[:5]
                        dep = cell[5:]
                        processed_rows.append({'Port': col, 'Type': 'ARR', 'Date': arr})
                        processed_rows.append({'Port': col, 'Type': 'DEP', 'Date': dep})
                    else:
                        # 형식이 다르면 원본값 그대로 저장(필요시 주석 해제)
                        # processed_rows.append({'Port': col, 'Type': None, 'Date': cell})
                        pass

            # 데이터프레임 변환 및 저장
            if processed_rows:
                processed_df = pd.DataFrame(processed_rows)
                processed_filename = f"{vessel_name_list[0]}_schedule_processed.xlsx"
                processed_filepath = os.path.join(self.download_dir, processed_filename)
                processed_df.to_excel(processed_filepath, index=False)
                print(f"ARR/DEP 전처리 엑셀 저장 완료: {processed_filepath}")

        self.Close()

        
