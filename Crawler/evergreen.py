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
import time, os

import openpyxl

class EVERGREEN_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "EMC"

    def run(self):
        # 0. 선사 홈페이지 접속
        self.Visit_Link("https://ss.shipmentlink.com/tvs2/jsp/TVS2_VesselSchedule.jsp")
        driver = self.driver
        wait = self.wait

        # 쿠키 뜨는 경우 //*[@id="btn_cookie_accept_all"]
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="btn_cookie_accept_all"]'
            )))
            cookie_btn.click()
        except:
            pass

        vessel_name_list = ["EVER LUCID","EVER ELITE","EVER LASTING","EVER VIM"]

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

            # ====== 항차번호(span[text]) 추출 ======
            # span[1], span[3], span[5], ... 순회
            table_titles = []
            span_idx = 1
            while True:
                try:
                    span_xpath = f'//*[@id="schedule"]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/span[{span_idx}]'
                    span_elem = driver.find_element(By.XPATH, span_xpath)
                    table_titles.append(span_elem.text.strip())
                    span_idx += 2
                except:
                    break  # 더 이상 span이 없으면 종료

            # ====== 테이블 데이터 수집 ======
            all_tables = []
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

                    # 테이블 데이터 + 항차번호 함께 저장
                    voyage = table_titles[table_idx - 1] if table_idx - 1 < len(table_titles) else ""
                    all_tables.append({"voyage": voyage, "table": table_data})
                    table_idx += 1
                except Exception:
                    # 더 이상 table이 없으면 break
                    break

            # ====== 데이터 저장 ======
            # 테이블별로 DataFrame 변환 후 concat
            if all_tables:
                df_list = []
                for item in all_tables:
                    table = item["table"]
                    voyage = item["voyage"]
                    if len(table) == 2:
                        df = pd.DataFrame([table[1]], columns=table[0])
                        df["항차번호"] = voyage
                        df_list.append(df)
                if df_list:
                    result_df = pd.concat(df_list, ignore_index=True)
                    save_path = self.get_save_path(self.carrier_name, vessel_name)
                    result_df.to_excel(save_path, index=False)
                    print(f"엑셀 저장 완료: {save_path}")

                    # openpyxl로 wrapText 활성화 (헤더는 제외)
                    wb = openpyxl.load_workbook(save_path)
                    ws = wb.active
                    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
                        for cell in row:
                            cell.alignment = openpyxl.styles.Alignment(wrap_text=True)
                    wb.save(save_path)
                    print("텍스트 줄바꿈(wrapText) 활성화 완료")

                    # =========================
                    # 1. ARRDEP 전처리 추가
                    # =========================
                    processed_rows = []
                    for idx, row in result_df.iterrows():
                        voyage = row.get("항차번호", "")
                        for col in result_df.columns:
                            if col == "항차번호":
                                continue
                            cell = row[col]
                            # ARRDEP 형식인지 체크
                            if isinstance(cell, str) and len(cell) == 9 and cell.count('/') == 2:
                                eta = cell[:5]
                                etd = cell[5:]
                                processed_rows.append({'항차번호': voyage, 'Port': col, 'Type': 'ETA', 'Date': eta})
                                processed_rows.append({'항차번호': voyage, 'Port': col, 'Type': 'ETD', 'Date': etd})
                            else:
                                # 형식이 다르면 원본값 그대로 저장(필요시 주석 해제)
                                # processed_rows.append({'항차번호': voyage, 'Port': col, 'Type': None, 'Date': cell})
                                pass

                    # 데이터프레임 변환 및 저장
                    if processed_rows:
                        processed_df = pd.DataFrame(processed_rows)
                        processed_path = self.get_save_path(self.carrier_name, vessel_name_list[0], ext="processed.xlsx")
                        processed_df.to_excel(processed_path, index=False)
                        print(f"ARR/DEP 전처리 엑셀 저장 완료: {processed_path}")

                        # wrapText 활성화 (헤더 제외)
                        wb2 = openpyxl.load_workbook(processed_path)
                        ws2 = wb2.active
                        for row in ws2.iter_rows(min_row=2, max_row=ws2.max_row, min_col=1, max_col=ws2.max_column):
                            for cell in row:
                                cell.alignment = openpyxl.styles.Alignment(wrap_text=True)
                        wb2.save(processed_path)
                        print("ARR/DEP 전처리 파일에도 wrapText 적용 완료")

        self.Close()
