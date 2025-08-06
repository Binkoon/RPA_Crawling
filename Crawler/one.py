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
import logging
import traceback

from datetime import datetime

class ONE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "ONE"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["MARIA C", "NYK DANIELLA","ONE REASSURANCE" ,"SAN FRANCISCO BRIDGE","ONE MARVEL"]
        
        # 크롤링 결과 추적
        self.success_count = 0
        self.fail_count = 0
        self.failed_vessels = []

    def setup_logging(self):
        """로깅 설정"""
        # 초기에는 에러가 없으므로 파일 로그 생성하지 않음
        self.logger = self.setup_logging(self.carrier_name, has_error=False)
        
    def setup_logging_with_error(self):
        """에러 발생 시 로깅 설정"""
        # 에러가 발생했으므로 파일 로그 생성
        self.logger = self.setup_logging(self.carrier_name, has_error=True)

    # 선박별 파라미터 매핑 (URL에 맞게 조정)
    vessel_params = {
        "ONE REASSURANCE": {"vslCdParam": "RSCT", "vslEngNmParam": "ONE+REASSURANCE+%28RSCT%29"},
        "SAN FRANCISCO BRIDGE": {"vslCdParam": "SFDT", "vslEngNmParam": "SAN+FRANCISCO+BRIDGE+%28SFDT%29"},
        "ONE MARVEL": {"vslCdParam": "ONMT", "vslEngNmParam": "ONE+MARVEL+%28ONMT%29"},
        "MARIA C": {"vslCdParam": "RCMT", "vslEngNmParam": "MARIA+C+%28RCMT%29"},
        "NYK DANIELLA": {"vslCdParam": "NDLT", "vslEngNmParam": "NYK+DANIELLA+%28NDLT%29"}
    }

    def step1_visit_website_with_vessel_params(self):
        """1단계: 지정된 선박별로 url param값만 변경하는 식으로 선사 홈페이지 접속"""
        try:
            self.logger.info("=== 1단계: 선박별 URL 파라미터로 홈페이지 접속 시작 ===")
            
            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 접속 시작")
                    
                    # 0. 선사 접속 (동적 URL 생성)
                    params = self.vessel_params[vessel_name]
                    url = f"https://ecomm.one-line.com/one-ecom/schedule/vessel-schedule?vslCdParam={params['vslCdParam']}&vslEngNmParam={params['vslEngNmParam']}&f_cmd="
                    self.Visit_Link(url)
                    driver = self.driver
                    wait = self.wait
                    time.sleep(3)  # 초기 로딩 대기
                    
                    self.logger.info(f"선박 {vessel_name} 접속 완료")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 접속 실패: {str(e)}")
                    self.fail_count += 1
                    self.failed_vessels.append(vessel_name)
                    continue
            
            self.logger.info("=== 1단계: 선박별 URL 파라미터로 홈페이지 접속 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 1단계: 선박별 URL 파라미터로 홈페이지 접속 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step2_download_pdf_files(self):
        """2단계: pdf파일로 다운로드"""
        try:
            self.logger.info("=== 2단계: PDF 파일 다운로드 시작 ===")
            
            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} PDF 다운로드 시작")
                    
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
                        self.logger.info("PDF 다운로드 옵션 선택 완료")
                        time.sleep(0.5)

                        download_pdf = wait.until(EC.element_to_be_clickable((
                            By.XPATH, '//*[@id="headlessui-dialog-:ra:"]/div[2]/div[3]/button[3]'
                        )))
                        driver.execute_script("arguments[0].scrollIntoView(true);", download_pdf)  # 요소를 화면에 보이게
                        driver.execute_script("arguments[0].click();", download_pdf)  # JS로 클릭
                    except Exception as e:
                        self.logger.error(f"모달 또는 Download 버튼 클릭 중 오류 발생 ({vessel_name}): {e}")

                    # 3. 다운로드 대기
                    time.sleep(4)
                    
                    self.success_count += 1
                    self.logger.info(f"선박 {vessel_name} PDF 다운로드 완료")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} PDF 다운로드 실패: {str(e)}")
                    self.fail_count += 1
                    self.failed_vessels.append(vessel_name)
                    continue
            
            self.logger.info("=== 2단계: PDF 파일 다운로드 완료 ===")
            self.logger.info(f"성공: {self.success_count}개, 실패: {self.fail_count}개")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 2단계: PDF 파일 다운로드 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step3_apply_naming_rules(self):
        """3단계: 파일명 규칙 + 저장 경로 규칙 적용 (아직 미구현이라 그냥 함수만 선언해놓고 일단 pass 처리 해두기)"""
        try:
            self.logger.info("=== 3단계: 파일명 규칙 및 저장경로 규칙 적용 시작 ===")
            
            # TODO: 파일명 규칙과 저장 경로 규칙 적용 로직 구현 필요
            # 현재는 기존 change_filename 로직을 활용하되, 향후 개선 예정
            for vessel_name in self.vessel_name_list:
                try:
                    self.change_filename(vessel_name)
                    self.logger.info(f"선박 {vessel_name} 파일명 변경 완료")
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 파일명 변경 실패: {str(e)}")
                    continue
            
            self.logger.info("=== 3단계: 파일명 규칙 및 저장경로 규칙 적용 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 3단계: 파일명 규칙 및 저장경로 규칙 적용 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def change_filename(self, vessel_name):
        """파일명 변경 함수 (기존 로직 유지)"""
        # 오늘 날짜 폴더
        target_dir = self.today_download_dir

        # ONE의 다운로드 파일명 패턴 (예: ONE Vessel Schedule 250718.pdf, ONE Vessel Schedule 250718 (1).pdf ...)
        today_str = datetime.now().strftime("%y%m%d")
        pattern = re.compile(rf"^ONE Vessel Schedule {today_str}(\s?\(\d+\))?\.pdf$")# ( \(\d+\))?는 (1), (2) 등의 번호도 매치시켜야함 ㅋ

        # 폴더 내 파일 전체 중 위 패턴과 맞는 것 찾기
        candidates = [f for f in os.listdir(target_dir) if pattern.match(f)]
        if not candidates:
            self.logger.warning("오늘자 ONE PDF 파일이 없습니다.")
            return
        
        # (여러개라면 방금 생성된 것 우선, mtime 정렬)
        candidates = sorted(candidates, key=lambda f: os.path.getmtime(os.path.join(target_dir, f)), reverse=True)
        old_file = os.path.join(target_dir, candidates[0])

        new_file = self.get_save_path('ONE', vessel_name, ext="pdf")
        # 이미 같은 이름 있다면 덮어쓰지 않게 예외처리
        if os.path.exists(new_file):
            os.remove(new_file)  # 또는, 뒤에 "_1" 등 붙여도 됨

        os.rename(old_file, new_file)
        self.logger.info(f"파일명 변경: {candidates[0]} → {os.path.basename(new_file)}")

    def run(self, vessel_name=None):
        """메인 실행 함수 (기존 호환성을 위해 vessel_name 파라미터 유지)"""
        return self.run_structured()

    def start_crawling(self):
        """기존 start_crawling 함수 (전체 선박용)"""
        # 선박 리스트 순회
        vessels = ["MARIA C", "NYK DANIELLA","ONE REASSURANCE" ,"SAN FRANCISCO BRIDGE","ONE MARVEL"] 
        for vessel in vessels:
            self.logger.info(f"크롤링 시작: {vessel}")
            self.run(vessel)
            self.change_filename(vessel)
            self.logger.info(f"크롤링 완료: {vessel}, 10초 대기...")
            time.sleep(10)  # 429 에러 방지 및 경고 팝업 대응
        
        self.Close()

    def run_structured(self):
        """구조화된 메인 실행 함수"""
        try:
            self.logger.info("=== ONE 크롤링 시작 ===")
            
            # 1단계: 지정된 선박별로 url param값만 변경하는 식으로 선사 홈페이지 접속
            if not self.step1_visit_website_with_vessel_params():
                return False
            
            # 2단계: pdf파일로 다운로드
            if not self.step2_download_pdf_files():
                return False
            
            # 3단계: 파일명 규칙 + 저장 경로 규칙 적용 (여기 아직 미구현이라 그냥 함수만 선언해놓고 일단 pass 처리 해두기)
            if not self.step3_apply_naming_rules():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== ONE 크롤링 완료 ===")
            self.logger.info(f"총 {len(self.vessel_name_list)}개 선박 중")
            self.logger.info(f"성공: {self.success_count}개")
            self.logger.info(f"실패: {self.fail_count}개")
            if self.failed_vessels:
                self.logger.info(f"실패한 선박: {', '.join(self.failed_vessels)}")
            
            self.Close()
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== ONE 크롤링 전체 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False