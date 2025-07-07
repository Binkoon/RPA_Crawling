# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/26
# 선사링크 : https://ss.shipmentlink.com/tvs2/jsp/TVS2_VesselSchedule.jsp
# 선박 리스트 : ["EVER LUCID"]

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
            tables = driver.find_elements(By.TAG_NAME, "table")

            all_data = []

            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    # td가 없는 tr(예: header)이면 건너뜀
                    if not cells:
                        continue
                    row_data = [cell.text.strip() for cell in cells]
                    all_data.append(row_data)

            # 2. 데이터프레임 변환 (컬럼명은 실제 테이블 구조에 맞게 수정 필요)
            df = pd.DataFrame(all_data)

            # 3. 엑셀로 저장
            excel_path = os.path.join(self.download_dir, f"{vessel_name}_schedule.xlsx")
            df.to_excel(excel_path, index=False, header=False)  # header 필요시 True로 변경

            print(f"엑셀 저장 완료: {excel_path}")

        self.Close()
