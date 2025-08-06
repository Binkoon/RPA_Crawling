# 선사 링크 : https://www.pilship.com/digital-solutions/
# 선박 리스트 : ["KGAA, KOTA GAYA"]
# 현재 미수행 - 전체 주석 처리

# from selenium.webdriver.common.by import By
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait
# import os,time
# import pandas as pd

# from .base import ParentsClass

# import datetime # 캘린더 있음.

# class PIL_Crawling(ParentsClass):
#     def __init__(self):
#         super().__init__()
#         self.carrier_name = "PIL"

#     def run(self):
#         # 0. 선사 접속
#         self.Visit_Link("https://www.pilship.com/digital-solutions/")
#         driver = self.driver
#         wait = self.wait
#         time.sleep(1)

#         # 0-1. 쿠키 허용 뜰 시,
#         try:
#             cookie_accept = wait.until(EC.element_to_be_clickable((
#                 By.XPATH , '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'
#             )))
#             cookie_accept.click()
#         except:
#             pass
        
#         time.sleep(1)
#         # 1. 스케줄 클릭 : //*[@id="schedules"]
#         schedule_btn = wait.until(EC.element_to_be_clickable((
#             By.XPATH , '//*[@id="schedules"]'
#         )))
#         time.sleep(0.5)
#         driver.execute_script("arguments[0].click()" , schedule_btn)
#         # schedule_btn.click()

#         # 2. by vessel 클릭 : //*[@id="e-n-tab-content-745373852 schedules-content"]/div/div[3]/div/div/div/ul/li[3]
#         by_vessel = wait.until(EC.element_to_be_clickable((
#             By.XPATH, '//*[@id="e-n-tab-content-745373852 schedules-content"]/div/div[3]/div/div/div/ul/li[3]'
#         )))
#         driver.execute_script("arguments[0].click()",by_vessel)
#         # by_vessel.click()

#         # 스크롤 다운 (y축으로 150픽셀)
#         driver.execute_script("window.scrollBy(0, 300);")
#         time.sleep(1)

#         time.sleep(1)
#         # 3. please select 클릭 : //*[@id="schedulesByVessel"]/div[1]/div/div[1]
#         vessel_select = wait.until(EC.element_to_be_clickable((
#             By.XPATH , '//*[@id="schedulesByVessel"]/div[1]/div/div[1]'
#         )))
#         vessel_select.click()

#         # 4. search input 클릭 : //*[@id="byvesseldropdownsearch"]
#         search_input = wait.until(EC.element_to_be_clickable((
#             By.XPATH, '//*[@id="byvesseldropdownsearch"]'
#         )))
#         search_input.click()
#         time.sleep(1)

#         # 5. vessel_list  // //*[@id="KGAA"]
#         vessel_name_list = ["KOTA GAYA"]
#         for vessel_name in vessel_name_list:
#             try:
#                 # 검색창에 vessel name 입력
#                 search_input.clear()
#                 for char in vessel_name:
#                     search_input.send_keys(char)
#                     time.sleep(0.1)
#                 time.sleep(1)  # 자동완성 리스트가 뜰 시간을 줌
                 
#                 # 자동완성 리스트에서 해당 vessel 클릭  <a class="custom-dd-op" id="KGAA"><span class="checkbox-port-text"><span class="highlight">KGAA, KOTA GAYA</span></span></a>
#                 vessel_option = wait.until(EC.element_to_be_clickable((
#                     By.ID , 'KGAA'
#                 )))
#                 vessel_option.click()
                
#                 print(f"선박 '{vessel_name}' 선택 완료")
#                 time.sleep(1)
                
#                 # //*[@id="schedulesByVessel"]/div[2]/div/div[1]/div[1]

#                 date_from = wait.until(EC.element_to_be_clickable((
#                     By.XPATH, '//*[@id="schedulesByVessel"]/div[2]/div/div[1]/div[1]'
#                 )))
#                 date_from.click()

#                 # # 오늘 날짜에서 3일 전 계산
#                 # today = datetime.datetime.now()
#                 # target_date = today - datetime.timedelta(days=3)
#                 # target_day = target_date.day

#                 # # 3일 전이 저번 달인지 확인
#                 # is_previous_month = target_date.month != today.month

#                 # try:
#                 #     if is_previous_month:
#                 #         # 저번 달인 경우 "old day" 클래스 사용
#                 #         target_element = wait.until(EC.element_to_be_clickable((
#                 #             By.XPATH, f'//td[contains(@class, "old day") and text()="{target_day}"]'
#                 #         )))
#                 #     else:
#                 #         # 같은 달인 경우 일반 "day" 클래스 사용
#                 #         target_element = wait.until(EC.element_to_be_clickable((
#                 #             By.XPATH, f'//td[contains(@class, "day") and not(contains(@class, "old")) and text()="{target_day}"]'
#                 #         )))
                    
#                 #     target_element.click()
#                 #     print(f"날짜 선택 완료: {target_date.strftime('%Y-%m-%d')}")
                
#                 # except Exception as e:
#                 #     print(f"날짜 선택 중 오류 발생: {str(e)}")


#             except Exception as e:
#                 print(f"선박 '{vessel_name}' 처리 중 오류 발생: {str(e)}")
#                 continue



#         self.Close()