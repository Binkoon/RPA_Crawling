# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/07/07 (완성)
# 선사 링크 : https://ebiz.pcsline.co.kr/
# 선박 리스트 : ["PEGASUS PETA","PEGASUS TERA","PEGASUS GLORY"]

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

import os,time
import pandas as pd

from .base import ParentsClass

class DYLINE_Crawling(ParentsClass):
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
        # 0. 선사 접속 링크
        self.Visit_Link("https://ebiz.pcsline.co.kr/")
        driver = self.driver
        wait = self.wait

        # 1. 스케줄 클릭 //*[@id="mf_wfm_header_gen_firstGenerator_0_btn_menu1_Label"]
        scheduel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="mf_wfm_header_gen_firstGenerator_0_btn_menu1_Label"]'
        )))
        scheduel_tab.click() # 만약 못알아먹으면 JS로 바꿔서 ㄱ
        time.sleep(0.5)

        # 2. 선박별 클릭  //*[@id="mf_wfm_header_grp_ul"]/li[1]/dl/dd[2]/a
        vessel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="mf_wfm_header_grp_ul"]/li[1]/dl/dd[2]/a'
        )))
        vessel_tab.click()
        time.sleep(0.5)

        # 3. 선박명 INPUT 클릭 //*[@id="mf_tac_layout_contents_00010004_body_ibx_vsl_input"]
        vessel_name_list = ["PEGASUS PETA"]
        
        for vessel_name in vessel_name_list:
            all_rows = []
            vessel_input = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_ibx_vsl_input"]'
            )))
            # 얘 그냥 셀레니움 click, send_keys로는 안됌. 이런 경우는 js로 ㄱㄱ
            driver.execute_script("arguments[0].click();", vessel_input)
            driver.execute_script("arguments[0].value = '';", vessel_input)
            driver.execute_script(f"arguments[0].value = '{vessel_name}';", vessel_input)
            driver.execute_script(
                "var event = new Event('input', { bubbles: true }); arguments[0].dispatchEvent(event);",
                vessel_input
            )
            time.sleep(1)
            autocomplete_item = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_ibx_vsl_itemTable_0"]'
            )))
            driver.execute_script("arguments[0].click();", autocomplete_item)
            time.sleep(1)

            # 항차번호 드롭다운 반복
            index = 1
            while True:
                try:
                    # 드롭다운 버튼 클릭 (조회 후마다 다시 열기)  //*[@id="mf_tac_layout_contents_00010004_body_ibx_voy_button"]
                    voy_dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_ibx_voy_button"]')))
                    driver.execute_script("arguments[0].click();", voy_dropdown_btn)
                    time.sleep(0.5)

                    # 항차 tr 클릭  //*[@id="mf_tac_layout_contents_00010004_body_ibx_voy_itemTable_main"]/tbody/tr[1]
                    tr_xpath = f'//*[@id="mf_tac_layout_contents_00010004_body_ibx_voy_itemTable_main"]/tbody/tr[{index}]'
                    voyage_tr = wait.until(EC.element_to_be_clickable((By.XPATH, tr_xpath)))
                    # driver.execute_script("arguments[0].click();", voyage_tr)
                    voyage_tr.click()
                    time.sleep(0.5)

                    # 조회 버튼 클릭
                    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_tac_layout_contents_00010004_body_btn_inq"]')))
                    search_btn.click()
                    time.sleep(1)

                    # 테이블 데이터 추출
                    tbody_xpath = '//*[@id="mf_tac_layout_contents_00010004_body_grd_cur_body_tbody"]'
                    tbody = wait.until(EC.presence_of_element_located((By.XPATH, tbody_xpath)))
                    tr_list = tbody.find_elements(By.XPATH, './tr')
                    time.sleep(0.5)

                    for tr in tr_list:
                        td_list = tr.find_elements(By.TAG_NAME, 'td')
                        row_data = [td.text.strip() for td in td_list]
                        # 선박명, 항차 인덱스 함께 저장
                        row_data.insert(0, vessel_name)
                        row_data.append(str(index))
                        all_rows.append(row_data)
                    
                    time.sleep(1)

                    index += 1
                except Exception:
                    # 더 이상 항차 tr이 없으면 break
                    break

        # 컬럼명 예시 (실제 테이블 구조에 맞게 수정)
        columns = ['Vessel', 'No','Port','Skip','Terminal','ETA-Day','ETA-Date','ETA-Time','ETD-Day','ETD-Date','ETD-Time','Remark','VoyageIndex']
        df = pd.DataFrame(all_rows, columns=columns[:len(all_rows[0])])
        save_path = os.path.join(self.download_dir, 'result.xlsx')
        df.to_excel(save_path, index=False)
        print(f"엑셀 저장 완료: {save_path}")

        self.Close()