# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/06/27 (완성)
# 선사링크 : "https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByVesselName"  -> 한국 홈페이지는 조회 X.  본사랑 다름
# 공동운항 선박 리스트 : "XIN NAN SHA", "XIN RI ZHAO", "XIN WU HAN", "XIN FANG CHENG"
# 추가 정보 : Cosco는 일반 크롤링 접근 막아놨음.  user-agent 필수. __init__ 코드 확인.

################# User-agent 모듈 ###############
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
############### 셀레니움 기본 + time #####
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
######## 부모클래스
from .base import ParentsClass
######### 데이터 저장

import os
import pandas as pd
from datetime import datetime
import logging
import traceback

class Cosco_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()
        self.carrier_name = "COS"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_list = ["XIN NAN SHA", "XIN RI ZHAO", "XIN WU HAN", "XIN FANG CHENG"]
        
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

    def step1_visit_website(self):
        """1단계: 선사 홈페이지 접속"""
        try:
            self.logger.info("=== 1단계: 선사 홈페이지 접속 시작 ===")
            
            # TARGET 페이지로 바로 접속
            self.Visit_Link("https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByVesselName")
            driver = self.driver
            wait = self.wait
            
            # 입력창 찾기
            input_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[1]/div/div/div/div[1]/input'
            vessel_input = wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
            
            self.logger.info("=== 1단계: 선사 홈페이지 접속 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 1단계: 선사 홈페이지 접속 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step2_crawl_vessel_data(self):
        """2단계: 지정된 선박 리스트 반복해서 조회"""
        try:
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
            driver = self.driver
            wait = self.wait
            
            # 입력창 찾기
            input_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[1]/div/div/div/div[1]/input'
            vessel_input = wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))

            for vessel_name in self.vessel_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    vessel_input.clear()
                    vessel_input.click()
                    vessel_input.send_keys(vessel_name)
                    self.logger.info(f"입력: {vessel_name}")
                    time.sleep(1)  # 자동완성 등 반응 대기

                    # 자동완성 드롭다운 항목 클릭
                    dropdown_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[1]/div/div/div[1]/div[2]/ul[2]/div/li'
                    dropdown_item = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
                    dropdown_item.click()
                    self.logger.info("자동완성 리스트 클릭")

                    # Search 버튼 클릭
                    search_btn_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[2]/button'
                    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, search_btn_xpath)))
                    search_button.click()
                    self.logger.info("Search 버튼 클릭")

                    # 조회 시, 새 웹페이지가 떠서 선박 스케줄 스크래핑 후 다시 이전 페이지로 가서 루핑 돌려야할 때의 코드.
                    time.sleep(2)
                    original_window = driver.current_window_handle
                    all_windows = driver.window_handles

                    for handle in all_windows:
                        if handle != original_window:
                            driver.switch_to.window(handle)
                            break

                     # PDF 다운로드 버튼 클릭
                    pdf_btn_xpath = '//*[@id="downloadSaislingSchedule"]/div[6]/p/span[3]/i'
                    pdf_button = wait.until(EC.element_to_be_clickable((By.XPATH, pdf_btn_xpath)))
                    pdf_button.click()
                    self.logger.info("PDF 다운로드 버튼 클릭")

                    # 파일 다운로드 대기 (충분히 여유를 줘야 함, 예: 5초)
                    time.sleep(5)

                    self.Visit_Link("https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByVesselName")
                    driver = self.driver
                    wait = self.wait
                    # 입력창 찾기
                    input_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[1]/div/div/div/div[1]/input'
                    vessel_input = wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))

                    time.sleep(1)
                    
                    self.logger.info(f"선박 {vessel_name} 크롤링 완료")
                    self.success_count += 1
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패: {str(e)}")
                    self.fail_count += 1
                    self.failed_vessels.append(vessel_name)
                    continue
            
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 완료 ===")
            self.logger.info(f"성공: {self.success_count}개, 실패: {self.fail_count}개")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 2단계: 선박별 데이터 크롤링 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step3_process_downloaded_files(self):
        """3단계: 파일 다운로드 후 지정한 경로로 저장 및 파일명 변경"""
        try:
            self.logger.info("=== 3단계: 파일 처리 및 파일명 변경 시작 ===")
            
            # 파일명 일괄 변경
            pdf_files = [f for f in os.listdir(self.today_download_dir) if f.lower().endswith('.pdf')]
            pdf_files.sort()
            
            for i, vessel_name in enumerate(self.vessel_list):
                if i < len(pdf_files):
                    old_path = os.path.join(self.today_download_dir, pdf_files[i])
                    new_filename = f"COSCO_{vessel_name}.pdf"
                    new_path = os.path.join(self.today_download_dir, new_filename)
                    os.rename(old_path, new_path)
                    self.logger.info(f"파일명 변경: {pdf_files[i]} → {new_filename}")
            
            self.logger.info("=== 3단계: 파일 처리 및 파일명 변경 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 3단계: 파일 처리 및 파일명 변경 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def run(self):
        """메인 실행 함수"""
        try:
            self.logger.info("=== COSCO 크롤링 시작 ===")
            
            # 1단계: 선사 홈페이지 접속
            if not self.step1_visit_website():
                return False
            
            # 2단계: 지정된 선박 리스트 반복해서 조회
            if not self.step2_crawl_vessel_data():
                return False
            
            # 3단계: 파일 다운로드 후 지정한 경로로 저장 및 파일명 변경
            if not self.step3_process_downloaded_files():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== COSCO 크롤링 완료 ===")
            self.logger.info(f"총 {len(self.vessel_list)}개 선박 중")
            self.logger.info(f"성공: {self.success_count}개")
            self.logger.info(f"실패: {self.fail_count}개")
            if self.failed_vessels:
                self.logger.info(f"실패한 선박: {', '.join(self.failed_vessels)}")
            
            self.Close()
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== COSCO 크롤링 전체 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False
        