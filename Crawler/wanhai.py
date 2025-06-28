# 선사링크 : https://www.wanhai.com/views/Main.xhtml
# 선박 대상 : ["WAN HAI 502","WAN HAI 521","WAN HAI 522"]
# wanhai는 크롤링으로 의심되면 CAPTCHA 씀. 처음부터 막는게 아니라, 감시하다 막음
# user-agent 활용

############ 셀레니움 ###############
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
################# User-agent 모듈 ###############
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
##############부모 클래스 ##############
from .base import ParentsClass
############# Schedule_Data쪽에 넘겨야함 ###########
import os
import pandas as pd
from datetime import datetime

class WANHAI_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.subfolder_name = self.__class__.__name__.replace("_crawling", "").lower()
        self.download_dir = os.path.join(self.base_download_dir, self.subfolder_name)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)


    def run(self):
        # 0. 선사 링크 접속
        self.Visit_Link("https://www.wanhai.com/views/Main.xhtml")
        driver = self.driver
        wait = self.wait

        # 1. Vessel Tracking 탭 클릭
        vessel_tracking_tab = wait.until(EC.element_to_be_clickable ((
            By.XPATH , '//*[@id="tabs"]/ul/li[4]'
        )))  
        vessel_tracking_tab.click()

        # 2. Vessel name 드랍다운 선택 ㄱㄱ
        vessel_dropdown = wait.until(EC.element_to_be_clickable ((
            By.XPATH , '//*[@id="skdByVslBean"]/select'
        )))

        select = Select(vessel_dropdown)

        ######### 홈페이지 구조 분석할떄, readonly가 있으면 그거 해제시켜줘야함
        # 해당 로직은 여기에 작성 #
        ##############################

        # 3. 선박명 루핑 시킴
        vessel_name_list = ['WAN HAI 502']
        for vessel_name in vessel_name_list:
            select.select_by_visible_text(vessel_name)

            submit_button = wait.until(EC.element_to_be_clickable ((
                By.XPATH , '//*[@id="quick_skd_vsl_query"]'
            )))

            submit_button.click()

            # 4. 스케줄 테이블 딱 봐주고
            result_table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="popuppane"]/table[3]'))
            )
            # 특정 tbody의 절대경로 (예: 제공한 HTML 기준으로 가정)
            target_tbody = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="popuppane"]/table[3]/tbody')))
            trs = target_tbody.find_elements(By.TAG_NAME, "tr")

            # 헤더 추출 (첫 번째 tr의 th)
            header_tr = trs[0]
            columns = [th.get_attribute("innerText").strip() for th in header_tr.find_elements(By.TAG_NAME, "th")]

            # 데이터 추출 (오늘 날짜 기준)
            today = datetime.now().date()
            table_data = []
            for tr in trs[1:]:  # 헤더 제외
                tds = tr.find_elements(By.TAG_NAME, "td")
                if len(tds) > 2:
                    eta_str = tds[2].get_attribute("innerText").strip()  # ETA는 3번째 칼럼 가정
                    try:
                        eta_date = datetime.strptime(eta_str, "%Y/%m/%d").date()
                        if eta_date >= today:
                            row_data = [td.get_attribute("innerText").strip() for td in tds]
                            table_data.append(row_data)
                    except ValueError:
                        continue

            df = pd.DataFrame(table_data, columns=columns)
            today_str = datetime.now().strftime("%Y%m%d")
            vessel_filename = vessel_name.replace(" ", "_")
            excel_path = os.path.join(self.download_dir, f"{today_str}{vessel_filename}.xlsx")
            df.to_excel(excel_path, index=False)
            print(f"엑셀 저장 완료: {excel_path}")

        self.Close()