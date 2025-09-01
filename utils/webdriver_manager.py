# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/01/27
# 역할 : WebDriver 설정 및 관리를 담당하는 클래스

import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

class WebDriverManager:
    """WebDriver 설정 및 관리를 담당하는 클래스"""
    
    def __init__(self, download_dir: str):
        self.download_dir = download_dir
        self.driver = None
        self.wait = None
    
    def setup_chrome_options(self) -> Options:
        """Chrome 옵션 설정"""
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # User-Agent 설정
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
        chrome_options.add_argument(f"--user-agent={user_agent}")
        
        # 다운로드 경로 설정
        prefs = {"download.default_directory": self.download_dir}
        chrome_options.add_experimental_option("prefs", prefs)
        
        return chrome_options
    
    def create_driver(self):
        """WebDriver 생성"""
        chrome_options = self.setup_chrome_options()
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        return self.driver, self.wait
    
    def close_driver(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
    
    def visit_link(self, url: str):
        """URL 방문"""
        if self.driver:
            self.driver.get(url)
