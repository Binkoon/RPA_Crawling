# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/07/01 (완성)
# 선사링크 : https://www.wanhai.com/views/Main.xhtml
# 선박 대상 : ["WAN HAI 502","WAN HAI 521","WAN HAI 522","WAN HAI 351","WAN HAI 377","WAN HAI 322"]
# 추가 정보 : wanhai는 크롤링으로 의심되면 CAPTCHA 씀. 처음부터 막는게 아니라, 감시하다 막음. 따라서 잦은 호출은 금지.

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
        # 0. 선사 링크 접속
        self.Visit_Link("https://www.wanhai.com/views/skd/SkdByVsl.xhtml")
        driver = self.driver
        wait = self.wait
        
        time.sleep(0.5)
        
        # 1. 선박명 루핑 시킴  //*[@id="skdByVslBean"]/select   //*[@id="skdByVslBean"]/select
        vessel_name_list = ["WAN HAI 502","WAN HAI 521","WAN HAI 522","WAN HAI 351","WAN HAI 377","WAN HAI 322"]
        for vessel_name in vessel_name_list:
            # 1. select 박스 찾기 (By.xpath 사용 ㄱㄱ)
            select_elem = wait.until(lambda d: d.find_element(By.XPATH, '//*[@id="skdByVslBean"]/select'))
            select_box = Select(select_elem)

            # 2. 옵션 중에서 vessel_name과 일치하는 항목 선택
            found = False
            for option in select_box.options:
                if option.text.strip() == vessel_name:
                    select_box.select_by_visible_text(option.text)
                    print(f"선택된 옵션: {option.text}")
                    found = True
                    break
            if not found:
                print(f"{vessel_name} 옵션을 찾을 수 없습니다.")
                continue

            time.sleep(0.5)  # 선택 후 대기

            # 3. 조회 버튼 클릭
            query_btn = wait.until(lambda d: d.find_element(By.ID, 'Query'))
            query_btn.click()
            print(f"{vessel_name} 조회 버튼 클릭 완료")

            time.sleep(2)  # 결과 로딩 대기

            # 4. 테이블 데이터 추출
            table_xpath = '//*[@id="popuppane"]/table[3]'
            row_idx = 1
            data_rows = []
            while True:
                try:
                    row_xpath = f'{table_xpath}/tbody/tr[{row_idx}]'
                    row_elem = driver.find_element(By.XPATH, row_xpath)
                    cells = row_elem.find_elements(By.TAG_NAME, 'td')
                    row_data = [cell.text.strip() for cell in cells]
                    if row_data:  # 빈 행은 제외
                        data_rows.append(row_data)
                    row_idx += 1
                except Exception:
                    # 더 이상 tr이 없으면 break
                    break

            print(f"{vessel_name} 테이블 row 개수: {len(data_rows)}")

            # 5. 데이터프레임으로 저장 및 엑셀로 내보내기
            if data_rows:
                # 첫 번째 row가 헤더라면 아래 코드로 하기. 근데 WAN HAI는 첫 row부터 데이터임. (=tr)
                # header = data_rows[0]
                # df = pd.DataFrame(data_rows[1:], columns=header)
                # 첫 번째 row가 데이터라면,
                df = pd.DataFrame(data_rows)
                save_path = os.path.join(self.download_dir, f"{vessel_name}_schedule.xlsx")
                df.to_excel(save_path, index=False, header=False)
                print(f"{vessel_name} 엑셀 저장 완료: {save_path}")
            else:
                print(f"{vessel_name} 데이터 없음")


        self.Close()