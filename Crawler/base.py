from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

class ParentsClass:
    def __init__(self):
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")  # 해상도 고정 (1920x1080)
        
        self.driver = webdriver.Chrome(options=chrome_options)  # 옵션 적용
        self.wait = WebDriverWait(self.driver, 20)  # 20초 대기

    def Visit_Link(self, url):
        self.driver.get(url)

    def Close(self):
        self.driver.quit()  # url 파라미터 제거 (불필요)
