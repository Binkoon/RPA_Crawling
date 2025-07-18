# 선사 링크 : https://www.pilship.com/digital-solutions/
# 선박 리스트 : ["KOTA GAYA"]

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import os,time
import pandas as pd

from .base import ParentsClass

import datetime # 캘린더 있음.

class PIL_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "PIL"

    def run(self):
        # 0. 선사 접속
        self.Visit_Link("https://www.pilship.com/digital-solutions/")
        driver = self.driver
        wait = self.wait
        time.sleep(1)

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

        # # 2-1. 스크롤 액션 추가 (300px 아래로 스크롤)
        # driver.execute_script("window.scrollBy(0, 300);")
        # time.sleep(0.5)  # 스크롤 후 잠깐 대기 (필요시)

        # # 3. please select 클릭
        # select_vessel = wait.until(EC.element_to_be_clickable((
        #     By.XPATH, '//*[@id="schedulesByVessel"]/div[1]/div/div[1]'
        # )))
        # select_vessel.click()

        # vessel_name_list = ["KGAA, KOTA GAYA"]
        # # 4. vessel_name input
        # for vessel_name in vessel_name_list:
        #     # 4. 선박명 입력 드롭다운 클릭(JS)
        #     vessel_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="schedulesByVessel"]/div[1]/div/div[2]/div[1]')))
        #     driver.execute_script("arguments[0].click();", vessel_input)
        #     time.sleep(0.5)

        #     # 5. 선박명 입력 (send_keys로)
        #     vessel_input_box = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="byvesseldropdownsearch"]')))
        #     driver.execute_script("""
        #         arguments[0].value = arguments[1];
        #         arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        #         arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        #     """, vessel_input_box, vessel_name)
        #     time.sleep(1)

        #     # 6. 자동완성 리스트에서 해당 선박 선택(JS)
        #     vessel_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="KGAA"]')))
        #     driver.execute_script("arguments[0].click();", vessel_option)
        #     time.sleep(1)

        #     # 7. Data From 클릭(JS)  
        #     data_from = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="schedulesByVessel"]/div[2]/div/div[1]')))
        #     driver.execute_script("arguments[0].click();", data_from)
        #     time.sleep(0.5)

        #     # === 오늘 날짜(현재 선택된 날짜) 정보 파싱 ===
        #     today_td = wait.until(EC.presence_of_element_located(
        #         (By.CSS_SELECTOR, "td.today.day")
        #     )) 
        #     today_num = int(today_td.text.strip())

        #     # 달력의 년/월 추출
        #     calendar_title_xpath = '//*[@id="detailByVesselDatePicker"]/div/div[1]/table/thead/tr[1]/th[2]'
        #     calendar_title_elem = wait.until(EC.visibility_of_element_located((By.XPATH, calendar_title_xpath)))
        #     calendar_title_text = calendar_title_elem.text.strip()  # e.g. "July 2025"
        #     calendar_month = datetime.datetime.strptime(calendar_title_text, "%B %Y").month
        #     calendar_year = datetime.datetime.strptime(calendar_title_text, "%B %Y").year

        #     # 오늘의 전체 날짜객체 계산
        #     today_date = datetime.date(calendar_year, calendar_month, today_num)
        #     three_days_ago = today_date - datetime.timedelta(days=3)

        #     # 지금 보는 캘린더가 "three_days_ago"와 같은 월/년인지 체크
        #     if (three_days_ago.year != calendar_year) or (three_days_ago.month != calendar_month):
        #         # 월 달라졌으면 '이전달' 버튼 클릭해서 넘어가야 함
        #         prev_btn_xpath = '//*[@id="detailByVesselDatePicker"]/div/div[1]/table/thead/tr[2]/th[1]'
        #         while True:
        #             prev_btn = wait.until(EC.element_to_be_clickable((By.XPATH, prev_btn_xpath)))
        #             driver.execute_script("arguments[0].click();", prev_btn)
        #             time.sleep(0.5)
        #             calendar_title_elem = wait.until(EC.visibility_of_element_located((By.XPATH, calendar_title_xpath)))
        #             calendar_title_text = calendar_title_elem.text.strip()
        #             cal_month = datetime.datetime.strptime(calendar_title_text, "%B %Y").month
        #             cal_year = datetime.datetime.strptime(calendar_title_text, "%B %Y").year
        #             if cal_year == three_days_ago.year and cal_month == three_days_ago.month:
        #                 break

        #     # "3일 전" 날짜가 old day 클래스(저번달)면 old day로, 같은 달이면 그냥 day로 찾는다
        #     target_day = three_days_ago.day
        #     sel_target = None

        #     for class_selector in [f"td.old.day", f"td.day"]:
        #         tds = driver.find_elements(By.CSS_SELECTOR, class_selector)
        #         for td in tds:
        #             try:
        #                 # 일치하는 날짜 찾기
        #                 if td.text.strip() == str(target_day):
        #                     sel_target = td
        #                     break
        #             except Exception:
        #                 continue
        #         if sel_target:
        #             break

        #     if sel_target:
        #         driver.execute_script("""
        #             arguments[0].scrollIntoView({ block: "center" });
        #             arguments[0].click();
        #         """, sel_target)
        #         print(f"{three_days_ago.strftime('%Y-%m-%d')} 날짜 선택 완료")
        #         time.sleep(0.5)
        #     else:
        #         print(f"3일 전 날짜 {three_days_ago}를 달력에서 찾지 못했습니다.")


        #     # 8. Date to 선택
        #     date_to_btn = wait.until(EC.element_to_be_clickable(
        #         (By.XPATH, '//*[@id="schedulesByVessel"]/div[2]/div/div[2]')
        #     ))
        #     driver.execute_script("arguments[0].click();", date_to_btn)
        #     time.sleep(0.5)

        #     # === 현재 Date To 달력의 월/년 정보 추출 ===
        #     calendar_title_xpath = '//*[@id="detailByVesselDatePicker"]/div/div[1]/table/thead/tr[1]/th[2]'
        #     calendar_title_elem = wait.until(EC.visibility_of_element_located((By.XPATH, calendar_title_xpath)))
        #     calendar_title_text = calendar_title_elem.text.strip()  # e.g., "July 2025"
        #     calendar_month = datetime.datetime.strptime(calendar_title_text, "%B %Y").month
        #     calendar_year = datetime.datetime.strptime(calendar_title_text, "%B %Y").year

        #     # === 오늘 날짜 기준으로 28일 후 날짜 계산 ===
        #     today = datetime.date.today()
        #     target_date = today + datetime.timedelta(days=28)
        #     target_day = target_date.day
        #     target_month = target_date.month
        #     target_year = target_date.year

        #     # === 달이 다르면 다음달로 넘어가야 함 ===
        #     if calendar_year < target_year or (calendar_year == target_year and calendar_month < target_month):
        #         next_btn_xpath = '//*[@id="detailByVesselDatePicker"]/div/div[1]/table/thead/tr[2]/th[3]'
        #         while True:
        #             next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, next_btn_xpath)))
        #             driver.execute_script("arguments[0].click();", next_btn)
        #             time.sleep(0.5)
        #             calendar_title_elem = wait.until(EC.visibility_of_element_located((By.XPATH, calendar_title_xpath)))
        #             calendar_title_text = calendar_title_elem.text.strip()
        #             calendar_month = datetime.datetime.strptime(calendar_title_text, "%B %Y").month
        #             calendar_year = datetime.datetime.strptime(calendar_title_text, "%B %Y").year
        #             if calendar_year == target_year and calendar_month == target_month:
        #                 break

        #     # === Date To 날짜 선택 (td with day OR new day class) ===
        #     target_day_element = None
        #     # 1. 시도: td.new.day (다음달)
        #     for td in driver.find_elements(By.CSS_SELECTOR, "td.new.day"):
        #         if td.text.strip() == str(target_day):
        #             target_day_element = td
        #             break

        #     # 2. 시도 실패 시: td.day (같은 달)
        #     if not target_day_element:
        #         for td in driver.find_elements(By.CSS_SELECTOR, "td.day"):
        #             if td.text.strip() == str(target_day):
        #                 target_day_element = td
        #                 break

        #     # 3. 클릭
        #     if target_day_element:
        #         driver.execute_script("arguments[0].click();", target_day_element)
        #         print(f"[Date To] {target_date.strftime('%Y-%m-%d')} 선택 완료")
        #         time.sleep(0.5)
        #     else:
        #         print(f"28일 후 날짜 {target_date.strftime('%Y-%m-%d')}를 찾지 못했습니다")
        
        self.Close()