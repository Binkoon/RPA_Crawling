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
        # 하위폴더명 = py파일명(소문자)
        self.subfolder_name = self.__class__.__name__.replace("_crawling", "").lower()
        self.download_dir = os.path.join(self.base_download_dir, self.subfolder_name)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        # 크롬 옵션에 하위폴더 지정 (드라이버 새로 생성 필요)
        chrome_options = Options()
        chrome_options.add_argument("start-maximized")
        self.set_user_agent(chrome_options)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        prefs = {"download.default_directory": self.download_dir}
        chrome_options.add_experimental_option("prefs", prefs)
        # 기존 드라이버 종료 및 새 드라이버로 교체
        self.driver.quit()
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

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

        # 2-1. 스크롤 액션 추가 (300px 아래로 스크롤)
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(0.5)  # 스크롤 후 잠깐 대기 (필요시)

        # 3. please select 클릭
        select_vessel = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//*[@id="schedulesByVessel"]/div[1]/div/div[1]'
        )))
        select_vessel.click()

        vessel_name_list = ["KGAA, KOTA GAYA"]
        # 4. vessel_name input
        for vessel_name in vessel_name_list:
            # 4. 선박명 입력 드롭다운 클릭(JS)
            vessel_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="schedulesByVessel"]/div[1]/div/div[2]/div[1]')))
            driver.execute_script("arguments[0].click();", vessel_input)
            time.sleep(0.5)

            # 5. 선박명 입력 (send_keys로)
            vessel_input_box = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="byvesseldropdownsearch"]')))
            driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, vessel_input_box, vessel_name)
            time.sleep(1)

            # 6. 자동완성 리스트에서 해당 선박 선택(JS)
            vessel_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="KGAA"]')))
            driver.execute_script("arguments[0].click();", vessel_option)
            time.sleep(1)

            # 7. Data From 클릭(JS)  
            data_from = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="schedulesByVessel"]/div[2]/div/div[1]')))
            driver.execute_script("arguments[0].click();", data_from)
            time.sleep(0.5)
            # 8. 캘린더에서 오늘 기준 3일 전 클릭(JS)  //*[@id="detailByVesselDatePicker"]/div/div[1]/table/tbody  //*[@id="detailByVesselDatePicker"]/div/div[1]/table/tbody
            # 오늘 날짜는  class명이 <td class="today day" ~~~ 임
            # css 셀렉터로는 : #detailByVesselDatePicker > div > div.datepicker-days > table > tbody > tr:nth-child(2) > td.today.day
            # //*[@id="detailByVesselDatePicker"]/div/div[1]/table/tbody/tr[2]/td[5]   예를 들어 오늘날짜가 여기있다하면  tr[2]/td[5]를 기준으로 3일전꺼를 봐야함.
            # 단, 7월 1일이라고 가정했을때, 3일 뒤면  6월28일이다. 그럴떄는 현재 보고 있는 캘린더에서 //*[@id="detailByVesselDatePicker"]/div/div[1]/table/thead/tr[2]/th[1] 를 클릭 후 봐야함.
            # //*[@id="detailByVesselDatePicker"]/div/div[1]/table/tbody/tr[5]/td[7]  그떄의 6월 28일은 이런 xpath값을 가짐. 따라서, 이건 datetime 모듈을 써야할거 같음.
            today = datetime.date.today()
            three_days_ago = today - datetime.timedelta(days=3)
            target_day = three_days_ago.day
            target_month = three_days_ago.month
            target_year = three_days_ago.year

            # 캘린더의 월/년 정보 읽기
            # 2. 캘린더에서 월/년 정보 읽기
            calendar_title_xpath = '//*[@id="detailByVesselDatePicker"]/div/div[1]/table/thead/tr[1]/th[2]'
            calendar_title_elem = wait.until(EC.visibility_of_element_located((By.XPATH, calendar_title_xpath)))
            calendar_title_text = calendar_title_elem.text.strip()  # 예: "July 2025"
            calendar_month = datetime.datetime.strptime(calendar_title_text, "%B %Y").month
            calendar_year = datetime.datetime.strptime(calendar_title_text, "%B %Y").year

            # 3. 필요시 이전달 버튼 클릭 (월/년이 다르면)
            if calendar_month != target_month or calendar_year != target_year:
                prev_btn_xpath = '//*[@id="detailByVesselDatePicker"]/div/div[1]/table/thead/tr[2]/th[1]'
                prev_btn = wait.until(EC.element_to_be_clickable((By.XPATH, prev_btn_xpath)))
                driver.execute_script("arguments[0].click();", prev_btn)
                time.sleep(1)  # 이전달 버튼 클릭 후 캘린더 갱신 대기

                # 다시 월/년 정보 읽기 (반복문으로 만들 수도 있음)
                calendar_title_elem = wait.until(EC.visibility_of_element_located((By.XPATH, calendar_title_xpath)))
                calendar_title_text = calendar_title_elem.text.strip()
                calendar_month = datetime.datetime.strptime(calendar_title_text, "%B %Y").month
                calendar_year = datetime.datetime.strptime(calendar_title_text, "%B %Y").year

                # 만약 여러 달을 넘어야 한다면 반복문으로 prev_btn 클릭을 감싸야 함

            time.sleep(0.5)

            # 4. tbody에서 target_day 클릭(JS)
            js_code = """
            let calendarBody = document.querySelector('#detailByVesselDatePicker > div > div.datepicker-days > table > tbody');
            let targetDay = arguments[0];
            let found = false;
            for (let i = 0; i < calendarBody.children.length; i++) {
                let tr = calendarBody.children[i];
                for (let j = 0; j < tr.children.length; j++) {
                    let td = tr.children[j];
                    if (td.innerText.trim() == targetDay.toString() && td.classList.contains('day')) {
                        td.click();
                        found = true;
                        break;
                    }
                }
                if (found) break;
            }
            return found;
            """
            driver.execute_script(js_code, target_day)
            time.sleep(0.5)


        self.Close()