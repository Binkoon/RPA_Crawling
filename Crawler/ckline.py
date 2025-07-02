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

class CKLINE_Crawling(ParentsClass):
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
        vessel_name_list = ["SKY MOON" , "SKY FLOWER" , "SKY JADE" , "SKY TIARA" , "SUNWIN" , "SKY VICTORIA" , "VICTORY STAR", 
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
                files = os.listdir(self.download_dir)
                downloading = [f for f in files if f.endswith('.crdownload') or f.endswith('.tmp')]
                if not downloading:
                    break
                if time.time() - start_time > download_wait_time:
                    print("다운로드 대기 시간 초과")
                    break
                time.sleep(1)

            # 오늘 날짜
            today = datetime.today().strftime("%Y%m%d")

            # 다운로드 폴더에서 가장 최근 파일 찾기
            files = [os.path.join(self.download_dir, f) for f in os.listdir(self.download_dir)]
            files = [f for f in files if os.path.isfile(f)]
            if files:
                latest_file = max(files, key=os.path.getctime)
                ext = os.path.splitext(latest_file)[1]
                new_filename = f"{vessel_name}_{today}{ext}"
                new_filepath = os.path.join(self.download_dir, new_filename)
                os.rename(latest_file, new_filepath)
                print(f"파일명 변경 완료: {new_filename}")
            else:
                print("다운로드된 파일이 없습니다.")       
        
        self.Close()