# 선사명 : SITC
# 선사링크 : https://ebusiness.sitcline.com/#/home

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # 명시적 대기용
########### 아래는 자식클래스 (선사) 들 import 목록 ############
from .base import ParentsClass

class SITC_Crawling(ParentsClass):
    def run(self):
        self.Visit_Link("https://ebusiness.sitcline.com/#/home")


"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SITC_crawling:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def go_to_site(self):
        url = "https://ebusiness.sitcline.com/#/home"
        self.driver.get(url)

    def input_pol_pod(self, pol, pod):
        # 1. POL 입력창 찾기 (id, name, xpath 등 실제 요소에 맞게 수정)
        pol_input = self.wait.until(EC.presence_of_element_located((By.XPATH, 'POL_INPUT_XPATH')))
        pol_input.clear()
        pol_input.send_keys(pol)

        # 2. POD 입력창 찾기
        pod_input = self.wait.until(EC.presence_of_element_located((By.XPATH, 'POD_INPUT_XPATH')))
        pod_input.clear()
        pod_input.send_keys(pod)

        # 3. 조회 버튼 클릭 (버튼의 id, xpath 등 실제 값으로 수정)
        search_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, 'SEARCH_BUTTON_XPATH')))
        search_btn.click()

    def close(self):
        self.driver.quit()

    def run(self, pol, pod):
        try:
            self.go_to_site()
            self.input_pol_pod(pol, pod)
            # 이후 결과 테이블 추출 코드 작성
        finally:
            self.close()

"""