# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/06/28 (완성)
# 선사 링크 : https://www.one-line.com/en
# 선박 리스트 : ["ONE REASSURANCE" , "SAN FRANCISCO BRIDGE" ,"ONE MARVEL" , "MARIA C" , "NYK DANIELLA"]
# 추가 정보 : 크롤링 호출 잦을 시, 팝업 띄우고 경고함. 이런 경우는 10초 정도 기다렸다가 다시 돌릴 것.

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base import ParentsClass
import time
import os,re

from datetime import datetime

class ONE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "ONE"

    # 선박별 파라미터 매핑 (URL에 맞게 조정)
    vessel_params = {
        "ONE REASSURANCE": {"vslCdParam": "RSCT", "vslEngNmParam": "ONE+REASSURANCE+%28RSCT%29"}
        # "SAN FRANCISCO BRIDGE": {"vslCdParam": "SFDT", "vslEngNmParam": "SAN+FRANCISCO+BRIDGE+%28SFDT%29"},
        # "ONE MARVEL": {"vslCdParam": "ONMT", "vslEngNmParam": "ONE+MARVEL+%28ONMT%29"},
        # "MARIA C": {"vslCdParam": "RCMT", "vslEngNmParam": "MARIA+C+%28RCMT%29"},
        # "NYK DANIELLA": {"vslCdParam": "NDLT", "vslEngNmParam": "NYK+DANIELLA+%28NDLT%29"}
    }

    def change_filename(self, vessel_name):
        # 오늘 날짜 폴더
        target_dir = self.today_download_dir

        # ONE의 다운로드 파일명 패턴 (예: ONE Vessel Schedule 250718.pdf, ONE Vessel Schedule 250718 (1).pdf ...)
        today_str = datetime.now().strftime("%y%m%d")
        pattern = re.compile(rf"^ONE Vessel Schedule {today_str}( \(\d+\))?\.pdf$")  # ( \(\d+\))?는 (1), (2) 등의 번호도 매치

        # 폴더 내 파일 전체 중 위 패턴과 맞는 것 찾기
        candidates = [f for f in os.listdir(target_dir) if pattern.match(f)]
        if not candidates:
            print("오늘자 ONE PDF 파일이 없습니다.")
            return
        
        # (여러개라면 방금 생성된 것 우선, mtime 정렬)
        candidates = sorted(candidates, key=lambda f: os.path.getmtime(os.path.join(target_dir, f)), reverse=True)
        old_file = os.path.join(target_dir, candidates[0])

        new_file = self.get_save_path('ONE', vessel_name, ext="pdf")
        # 이미 같은 이름 있다면 덮어쓰지 않게 예외처리
        if os.path.exists(new_file):
            os.remove(new_file)  # 또는, 뒤에 "_1" 등 붙여도 됨

        os.rename(old_file, new_file)
        print(f"파일명 변경: {candidates[0]} → {os.path.basename(new_file)}")

    def run(self, vessel_name):
        # 0. 선사 접속 (동적 URL 생성)
        params = self.vessel_params[vessel_name]
        url = f"https://ecomm.one-line.com/one-ecom/schedule/vessel-schedule?vslCdParam={params['vslCdParam']}&vslEngNmParam={params['vslEngNmParam']}&f_cmd="
        self.Visit_Link(url)
        driver = self.driver
        wait = self.wait
        time.sleep(3)  # 초기 로딩 대기

        # 1. Download 버튼 클릭 (초기 버튼)
        download_btn_xpath = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//*[@id="__next"]/main/div[2]/div[2]/div[7]/div[1]/div[3]/div/div[2]/button'
        )))  # 
        driver.execute_script("arguments[0].click();", download_btn_xpath)  # JS로 클릭
        time.sleep(2)  # 모달 로딩 대기

        # 2. 모달 팝업 대기 및 Download 버튼 클릭
        try:
            # 모달이 나타날 때까지 대기
            # modal = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="headlessui-dialog-:ra:"]')))

            # PDF 라디오 버튼 클릭 (XPath는 상황에 따라 변수 처리 가능)
            pdf_radio = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="headlessui-dialog-:ra:"]/div[2]/div[2]/div[2]/label/div'
            ))) # //*[@id="headlessui-dialog-:ra:"]/div[2]/div[2]/div[2]/label/div
            # pdf_radio.click()
            driver.execute_script("arguments[0].click();",pdf_radio)
            print("PDF 다운로드 옵션 선택 완료")
            time.sleep(0.5)

            download_pdf = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="headlessui-dialog-:ra:"]/div[2]/div[3]/button[3]'
            )))
            driver.execute_script("arguments[0].scrollIntoView(true);", download_pdf)  # 요소를 화면에 보이게
            driver.execute_script("arguments[0].click();", download_pdf)  # JS로 클릭
        except Exception as e:
            print(f"모달 또는 Download 버튼 클릭 중 오류 발생 ({vessel_name}): {e}")

        # 3. 다운로드 대기
        time.sleep(4)
        

    def start_crawling(self):
        # 선박 리스트 순회
        vessels = ["ONE REASSURANCE"] #, "SAN FRANCISCO BRIDGE"] #, "ONE MARVEL", "MARIA C", "NYK DANIELLA"]
        for vessel in vessels:
            print(f"크롤링 시작: {vessel}")
            self.run(vessel)
            self.change_filename(vessel)
            print(f"크롤링 완료: {vessel}, 10초 대기...")
            time.sleep(10)  # 429 에러 방지 및 경고 팝업 대응
        
        
        self.Close()