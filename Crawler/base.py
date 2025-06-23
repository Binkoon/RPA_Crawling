# 각 선사별 공통 클래스를 정의한 부모 클래스 역할을 함
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class ParentsClass:
    def __init__(self):
        self.driver = webdriver.Chrome() # 크롬 기반으로 가져오는걸 원칙으로 정의
        self.wait = WebDriverWait(self.driver,20) # 일단 10초 대기를 디폴트로 잡고 자식 클래스에서 until 써서 상세 분류한다. -> 20초로 해봄.
    
    def Visit_Link(self,url):
        self.driver.get(url)

    def Close(self,url):
        self.driver.quit() # 브라우저 전체 종료