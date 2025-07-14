# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/30 (완성)
# 선사 링크 : https://es.ckline.co.kr/
# 선박 리스트 : 
"""
["SKY MOON" , "SKY FLOWER" , "SKY JADE" , "SKY TIARA" , "SUNWIN" , "SKY VICTORIA" , "VICTORY STAR", 
"SKY IRIS" , "SKY SUNSHINE" , "SKY RAINBOW" , "BAL BOAN" , "SKY CHALLENGE" ,"BEI HAI" ,"XIN TAI PING" , "SKY ORION"]
"""

# 추가 정보 : 선박이 꽤 많음. 다운로드 받다가 파일명 ReName에서 가끔 꼬일때가 있음. 수정 필요

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .base import ParentsClass
import time,os
from datetime import datetime
import re
import pandas as pd

class CKLINE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "CKL"


    def run(self):
        # 0. 웹사이트 방문
        self.Visit_Link("https://es.ckline.co.kr/")
        driver = self.driver
        wait = self.wait

        # 1. 로딩 화면 대기
        wait.until(EC.invisibility_of_element_located((By.ID, "mf_grp_loading")))

        # 2. 팝업 닫기
        pop_up_close = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_btn_noti"]')))
        pop_up_close.click()

        # 3. 스케줄 메뉴 클릭
        menu1 = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div/ul/li[1]')))
        menu1.click()
        time.sleep(0.5)  # 하위 메뉴 표시 대기

        # 4. 선박 메뉴 클릭
        submenu = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div/ul/li[1]/ul/li[2]')))
        submenu.click()
        print("메뉴 클릭 완료!")
        time.sleep(1)  # 페이지 로드 대기 시간 증가

        # 5. 선박별 드롭다운 처리
        vessel_name_list = ["SKY MOON", "SKY FLOWER" , "SKY JADE" , "SKY TIARA" , "SUNWIN" , "SKY VICTORIA" , "VICTORY STAR", 
                            "SKY IRIS" , "SKY SUNSHINE" , "SKY RAINBOW" , "BAL BOAN" , "SKY CHALLENGE" ,"BEI HAI" ,"XIN TAI PING" , "SKY ORION"]
        for vessel_name in vessel_name_list:
            # 1. 드롭다운(입력창) 클릭해서 리스트 활성화
            vessel_div = driver.find_element(By.ID, 'mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_button')
            vessel_div.click() # //*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_button"]
            time.sleep(0.5)

            # 2. 자동완성 리스트에서 tr 순회하며 클릭
            idx = 1
            found = False
            while True:
                try:
                    row_xpath = f'//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_itemTable_main"]/tbody/tr[{idx}]'
                    row_elem = driver.find_element(By.XPATH, row_xpath) # mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_itemTable_main
                    td_elem = row_elem.find_element(By.TAG_NAME, 'td')
                    vessel_text = td_elem.text.strip()
                    if vessel_text == vessel_name:
                        td_elem.click()
                        print(f"{vessel_name} 선택 완료 (index: {idx})")
                        found = True
                        break
                    idx += 1
                except Exception:
                    break  # 더 이상 tr이 없으면 종료
            if not found:
                print(f"{vessel_name} 자동완성 리스트에서 찾을 수 없음")
            time.sleep(1)  # 선택 후 대기

            # 조회 버튼 클릭요
            search_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_btn_inquiry"]'
            )))
            search_btn.click()
            time.sleep(1)

            # 다운로드 버튼 클릭이요
            download_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH ,'//*[@id="mf_wfm_intro_tac_layout_contents_WESSCH002_body_btn_trigger2"]'
            )))
            download_btn.click()
            time.sleep(1)

            # 다운로드가 완료될 때까지 대기 (.crdownload/.tmp 파일이 없어질 때까지)
            download_wait_time = 30  # 최대 30초 대기
            start_time = time.time()
            while True:
                files = os.listdir(self.today_download_dir)
                downloading = [f for f in files if f.endswith('.crdownload') or f.endswith('.tmp')]
                if not downloading:
                    break
                if time.time() - start_time > download_wait_time:
                    print("다운로드 대기 시간 초과")
                    break
                time.sleep(1)

        # 오늘 날짜
        today = datetime.today().strftime("%Y%m%d")

        self.Close()

        # === [다운로드 완료 후 후처리] ===

        # 1. 다운로드된 Vessel*.xlsx 파일 리스트 정렬
        files = [f for f in os.listdir(self.today_download_dir)
                 if f.startswith("Vessel") and f.lower().endswith('.xlsx')]
        files.sort()  # Vessel.xlsx, Vessel (1).xlsx, Vessel (2).xlsx ... 순서대로

        # 2. vessel_name_list와 1:1로 파일명 변경
        for i, vessel_name in enumerate(vessel_name_list):
            if i < len(files):
                old_path = os.path.join(self.today_download_dir, files[i])
                new_filename = f"{self.carrier_name}_{vessel_name}.xlsx"
                new_path = os.path.join(self.today_download_dir, new_filename)
                os.rename(old_path, new_path)
                print(f"파일명 변경: {files[i]} → {new_filename}")

        # 3. 파일명 변경 후 전처리
        for vessel_name in vessel_name_list:
            fpath = os.path.join(self.today_download_dir, f"{self.carrier_name}_{vessel_name}.xlsx")
            if os.path.exists(fpath):
                try:
                    df = pd.read_excel(fpath)
                    # 1. 'undefined' 컬럼명을 'Vessel Name'으로 변경
                    if 'undefined' in df.columns:
                        df.rename(columns={'undefined': 'Vessel Name'}, inplace=True)
                    # 2. 선박명/항차번호 분리 (첫 컬럼)
                    if 'Vessel Name' in df.columns:
                        split_df = df['Vessel Name'].str.extract(r'(?P<Vessel_Name>[A-Z\s]+)\s+(?P<D_Voy>[A-Z0-9.\-]+)')
                        df['Vessel Name'] = split_df['Vessel_Name']
                        df.insert(1, 'D-Voy', split_df['D_Voy'])

                    # 3. 컬럼명 한글 → 영문 변경
                    col_map = {
                        '지역': 'Port',
                        '입항일': 'ETA',
                        '출항일': 'ETD'
                    }
                    df.rename(columns=col_map, inplace=True)

                    # 4. 컬럼 순서 재정렬
                    desired_cols = ['Vessel Name', 'D-Voy', 'Port', 'ETA', 'ETD']
                    rest_cols = [col for col in df.columns if col not in desired_cols]
                    final_cols = desired_cols + rest_cols
                    df = df[final_cols]

                    # 5. 전처리된 파일로 덮어쓰기
                    df.to_excel(fpath, index=False)
                    print(f"전처리 및 컬럼명 변경 완료: {os.path.basename(fpath)}")
                except Exception as e:
                    print(f"전처리 중 오류({vessel_name}): {e}")