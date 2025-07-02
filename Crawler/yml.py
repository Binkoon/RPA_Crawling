# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/30 (완성)
# 선사 링크 : https://e-solution.yangming.com/e-service/Vessel_Tracking/SearchByVessel.aspx
# 선박 리스트 : ["YM CREDENTIAL" , "YM COOPERATION" ,"YM INITIATIVE"]

# https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel=YM%20CREDENTIAL|YCDL&&func=current&&LocalSite=
# https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel=YM%20COOPERATION|YCPR&&func=current&&LocalSite=
# https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel=YM%20INITIATIVE|YINT&&func=current&&LocalSite=

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from .base import ParentsClass
import os,time
from datetime import datetime

import pandas as pd

class YML_Crawling(ParentsClass):
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
        # 0. 선사 접근
        vessel_name_list = ["YM CREDENTIAL" , "YM COOPERATION" ,"YM INITIATIVE"]
        driver = self.driver
        wait = self.wait

        for vessel_name in vessel_name_list:
            vessel_name_param = vessel_name.replace(" ","%20") # 이걸로 대체해주셈. url parameter
            url = f'https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel={vessel_name_param}|YCDL&&func=current&&LocalSite='
            self.Visit_Link(url)
