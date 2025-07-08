# 선사 링크 : https://www.pilship.com/digital-solutions/
# 선박 리스트 : ["KOTA GAYA"]

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

import os,time
import pandas as pd

from .base import ParentsClass

class PIL_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()

    def run(self):
        # 0. 선사 접속
        self.Visit_Link("https://www.pilship.com/digital-solutions/")
        driver = self.driver
        wait = self.wait
        time.sleep(5)

        # 0-1. 쿠키 허용 뜰 시,
        try:
            cookie_accept = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'
            )))
            cookie_accept.click()
        except:
            pass

        # 1. 스케줄 탭 클릭
        schedule_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="schedules"]'
        )))
        schedule_tab.click()

        # 2. by vessel 클릭 //*[@id="e-n-tab-content-745373852 schedules-content"]/div/div[3]/div/div/div/ul/li[3]
        vessel_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="e-n-tab-content-745373852 schedules-content"]/div/div[3]/div/div/div/ul/li[3]'
        )))
        vessel_tab.click()

        # 3. please select 클릭
        select_vessel = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//*[@id="schedulesByVessel"]/div[1]/div/div[1]'
        )))
        select_vessel.click()

        vessel_name_list = ["KGAA, KOTA GAYA"]
        # 4. vessel_name input
        for vessel_name in vessel_name_list:
            # //*[@id="schedulesByVessel"]/div[1]/div/div[2]/div[1] <- 이거 클릭하되, JS로 해보기 (execute)
            # 선박 입력해주고, //*[@id="schedulesByVessel"]/div[1]/div/div[2]/div[2] 클릭
            # Data From //*[@id="schedulesByVessel"]/div[2]/div/div[1]  클릭해주고 캘린더에서 오늘날짜 기준, 3일전 날짜 클릭
            # Date to //*[@id="schedulesByVessel"]/div[3]/div/div[1]  클릭해주고 캘린더에서 오늘날짜 기준, 28일 후 날짜 클릭
            # search_btn 클릭 //*[@id="sbvSubmitBtn"]  .click()  위에 4개는 JS로.
            # 4. 선박명 입력 드롭다운 클릭(JS)
            vessel_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="schedulesByVessel"]/div[1]/div/div[2]/div[1]')))
            driver.execute_script("arguments[0].click();", vessel_input)
            time.sleep(0.5)

            # 5. 선박명 입력 (send_keys로)
            vessel_input_box = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Please select vessel"]')))
            vessel_input_box.clear()
            vessel_input_box.send_keys(vessel_name)
            time.sleep(1)

            # 6. 자동완성 리스트에서 해당 선박 선택(JS)
            vessel_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="schedulesByVessel"]/div[1]/div/div[2]/div[2]')))
            driver.execute_script("arguments[0].click();", vessel_option)
            time.sleep(1)

            # 7. Data From 클릭(JS)
            data_from = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="schedulesByVessel"]/div[2]/div/div[1]')))
            driver.execute_script("arguments[0].click();", data_from)
            time.sleep(0.5)
            # 8. 캘린더에서 오늘 기준 3일 전 클릭(JS)
            # 오늘 날짜 가져오기
            from datetime import datetime, timedelta
            three_days_ago = datetime.today() - timedelta(days=3)
            day_str = str(three_days_ago.day)
            # 날짜 선택 (동적 캘린더라면 XPath 조정 필요)
            calendar_day = wait.until(EC.element_to_be_clickable((By.XPATH, f'//div[contains(@class,"ant-picker-cell-inner") and text()="{day_str}"]')))
            driver.execute_script("arguments[0].click();", calendar_day)
            time.sleep(0.5)

            # 9. Data To 클릭(JS)
            data_to = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="schedulesByVessel"]/div[3]/div/div[1]')))
            driver.execute_script("arguments[0].click();", data_to)
            time.sleep(0.5)
            # 10. 캘린더에서 오늘 기준 28일 후 클릭(JS)
            twenty_eight_days = datetime.today() + timedelta(days=28)
            day_str_to = str(twenty_eight_days.day)
            calendar_day_to = wait.until(EC.element_to_be_clickable((By.XPATH, f'//div[contains(@class,"ant-picker-cell-inner") and text()="{day_str_to}"]')))
            driver.execute_script("arguments[0].click();", calendar_day_to)
            time.sleep(0.5)

            # 11. search_btn 클릭(JS)
            search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sbvSubmitBtn"]')))
            driver.execute_script("arguments[0].click();", search_btn)
            time.sleep(3)

            # 12. 결과 테이블에서 데이터 추출
            # (아래는 예시, 실제 테이블 구조에 맞게 XPATH 수정 필요)
            columns = ["Port", "ETA", "ETD", "Voyage", "Service"]
            data = []
            row_idx = 1
            while True:
                try:
                    tr = driver.find_element(By.XPATH, f'//*[@id="schedulesByVessel"]/div[4]/div/table/tbody/tr[{row_idx}]')
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) < len(columns):
                        break
                    row = [td.text.strip() for td in tds[:len(columns)]]
                    data.append(row)
                    row_idx += 1
                except Exception:
                    break

            df = pd.DataFrame(data, columns=columns)
            save_path = os.path.join(self.download_dir, f'{vessel_name}_schedule.xlsx')
            df.to_excel(save_path, index=False)
            print(f"[{vessel_name}] 엑셀 저장 완료: {save_path}")

        self.Close()