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

class WANHAI_Crawling(ParentsClass):       
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
        time.sleep(1)

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
            time.sleep(0.5)

            submit_button = wait.until(EC.element_to_be_clickable ((
                By.XPATH , '//*[@id="quick_skd_vsl_query"]'
            )))

            submit_button.click()

        # 4. ETA칼럼있는 쪽 본다음, 오늘 날짜 기준으로 아래꺼 뽑아주기
        # 절대경로 : //*[@id="popuppane"]/table[3] 이 테이블에서  //*[@id="popuppane"]/table[3]/tbody/tr[1]/th[3]  (ETA칼럼) 을 선택했을 때, 오늘 날짜인 애를 시작으로
        #    아래꺼 쫙 뽑아줘야함. 

        self.Close()