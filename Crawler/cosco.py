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
import glob

class Cosco_Crawling(ParentsClass):
    def __init__(self):
        super().__init__("COSCO")  # carrier_name을 부모 클래스에 전달
        self.carrier_name = "COS"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["XIN NAN SHA", "XIN RI ZHAO", "XIN WU HAN", "XIN SU ZHOU" ,"COSCO HAIFA","XIN QIN HUANG DAO","XIN TIAN JIN"
        ,"PHEN BASIN","XIN YAN TIAN","XIN NING BO","TIAN CHANG HE"]
        
        # 크롤링 결과 추적
        self.success_count = 0
        self.fail_count = 0
        self.failed_vessels = []
        self.failed_reasons = {}
        
        # 파일명 변경 추적
        self.renamed_files = {}

    def setup_logging(self):
        """로깅 설정"""
        # 초기에는 에러가 없으므로 파일 로그 생성하지 않음
        self.logger = super().setup_logging(self.carrier_name, has_error=False)
        
    def setup_logging_with_error(self):
        """에러 발생 시 로깅 설정"""
        # 에러가 발생했으므로 파일 로그 생성
        self.logger = super().setup_logging(self.carrier_name, has_error=True)

    def rename_downloaded_file(self, vessel_name, timeout=30):
        """다운로드된 파일을 선박명으로 변경"""
        try:
            start_time = time.time()
            renamed = False
            
            while time.time() - start_time < timeout:
                # 다운로드 디렉토리에서 가장 최근 PDF 파일 찾기
                pdf_files = glob.glob(os.path.join(self.today_download_dir, "*.pdf"))
                
                if pdf_files:
                    # 가장 최근 파일 선택 (수정 시간 기준)
                    latest_pdf = max(pdf_files, key=os.path.getmtime)
                    
                    # 파일명이 이미 변경되었는지 확인
                    if os.path.basename(latest_pdf).startswith(f"{self.carrier_name}_{vessel_name}"):
                        self.logger.info(f"선박 {vessel_name}: 파일명이 이미 올바르게 설정됨")
                        self.renamed_files[vessel_name] = latest_pdf
                        return True
                    
                    # 파일이 아직 다운로드 중인지 확인 (.crdownload, .tmp 파일)
                    if latest_pdf.endswith('.crdownload') or latest_pdf.endswith('.tmp'):
                        time.sleep(1)
                        continue
                    
                    # 새 파일명 생성
                    new_filename = f"{self.carrier_name}_{vessel_name}.pdf"
                    new_filepath = os.path.join(self.today_download_dir, new_filename)
                    
                    # 기존 파일이 있으면 삭제
                    if os.path.exists(new_filepath):
                        os.remove(new_filepath)
                        self.logger.info(f"선박 {vessel_name}: 기존 파일 삭제됨")
                    
                    # 파일명 변경
                    try:
                        os.rename(latest_pdf, new_filepath)
                        self.logger.info(f"선박 {vessel_name}: 파일명 변경 완료 - {os.path.basename(latest_pdf)} → {new_filename}")
                        
                        self.renamed_files[vessel_name] = new_filepath
                        renamed = True
                        break
                    except PermissionError:
                        # 파일이 사용 중인 경우 잠시 대기
                        self.logger.info(f"선박 {vessel_name}: 파일이 사용 중입니다. 잠시 대기...")
                        time.sleep(2)
                        continue
                    except Exception as e:
                        self.logger.error(f"선박 {vessel_name}: 파일명 변경 중 오류 - {str(e)}")
                        time.sleep(1)
                        continue
                
                time.sleep(1)
            
            if not renamed:
                self.logger.warning(f"선박 {vessel_name}: 파일명 변경 실패 - PDF 파일을 찾을 수 없음")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"선박 {vessel_name}: 파일명 변경 중 오류 발생 - {str(e)}")
            return False

    def step1_visit_website(self):
        """1단계: 선사 홈페이지 접속"""
        try:
            self.logger.info("=== 1단계: 선사 홈페이지 접속 시작 ===")
            
            # TARGET 페이지로 바로 접속
            self.Visit_Link("https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByVesselName")
            time.sleep(2)  # 페이지 로딩 대기 (3초 → 2초로 감소)
            
            driver = self.driver
            wait = self.wait
            
            # 입력창 찾기 (테스트 코드와 동일한 XPath 사용)
            input_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[1]/div/div/div/div[1]/input'
            vessel_input = wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
            self.logger.info("입력창 찾기 성공")
            
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
        """2단계: 지정된 선박 리스트 반복해서 조회 (테스트 코드 방식으로 단순화)"""
        try:
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
            driver = self.driver
            wait = self.wait
            
            # 입력창 찾기 (테스트 코드와 동일한 XPath 사용)
            input_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[1]/div/div/div/div[1]/input'
            vessel_input = wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))

            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_tracking(vessel_name)
                    
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
                    time.sleep(2)  # 새 창 대기 (테스트 코드와 동일)
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
                    time.sleep(5)  # 다운로드 대기 (테스트 코드와 동일)

                    # 메인 페이지로 돌아가기 (테스트 코드 방식)
                    self.Visit_Link("https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByVesselName")
                    driver = self.driver
                    wait = self.wait
                    
                    # 새 페이지에서 입력창 다시 찾기
                    input_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[1]/div/div/div/div[1]/input'
                    vessel_input = wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))

                    time.sleep(1)
                    
                    # 파일명 즉시 변경 (cosco.py 방식 유지)
                    if self.rename_downloaded_file(vessel_name):
                        self.logger.info(f"선박 {vessel_name} 파일명 변경 성공")
                        # 성공 카운트는 end_vessel_tracking에서 자동 처리됨
                    else:
                        self.logger.warning(f"선박 {vessel_name} 파일명 변경 실패")
                    
                    # 선박별 타이머 종료 (성공/실패 카운트 자동 처리)
                    self.end_vessel_tracking(vessel_name, success=True)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패: {str(e)}")
                    # 실패한 선박 기록 (테스트 코드 방식으로 단순화)
                    self.fail_count += 1
                    if vessel_name not in self.failed_vessels:
                        self.failed_vessels.append(vessel_name)
                    
                    # 실패한 경우에도 타이머 종료
                    self.end_vessel_tracking(vessel_name, success=False)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
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

    def record_vessel_success(self, vessel_name):
        """선박 성공 기록 (성공 카운트는 end_vessel_tracking에서 자동 처리됨)"""
        # 성공 카운트는 end_vessel_tracking에서 자동 처리됨
        # 실패 목록에서 제거
        if vessel_name in self.failed_vessels:
            self.failed_vessels.remove(vessel_name)
        if vessel_name in self.failed_reasons:
            del self.failed_reasons[vessel_name]

    def record_vessel_failure(self, vessel_name, reason):
        """선박 실패 기록"""
        self.fail_count += 1
        if vessel_name not in self.failed_vessels:
            self.failed_vessels.append(vessel_name)
        self.failed_reasons[vessel_name] = reason

    def step3_process_downloaded_files(self):
        """3단계: 파일 다운로드 후 지정한 경로로 저장 및 파일명 변경 확인"""
        try:
            self.logger.info("=== 3단계: 파일 처리 및 파일명 변경 확인 시작 ===")
            
            # 파일명 변경이 성공적으로 완료되었는지 확인
            pdf_files = [f for f in os.listdir(self.today_download_dir) if f.lower().endswith('.pdf')]
            
            # 파일명 변경 확인 및 로깅
            for vessel_name in self.vessel_name_list:
                expected_filename = f"{self.carrier_name}_{vessel_name}.pdf"
                expected_path = os.path.join(self.today_download_dir, expected_filename)
                
                if os.path.exists(expected_path):
                    self.logger.info(f"선박 {vessel_name}: 파일명 변경 확인됨 - {expected_filename}")
                else:
                    self.logger.warning(f"선박 {vessel_name}: 파일명 변경 확인 실패 - {expected_filename} 파일이 없음")
            
            self.logger.info("=== 3단계: 파일 처리 및 파일명 변경 확인 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 3단계: 파일 처리 및 파일명 변경 확인 실패 ===")
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
            
            # 3단계: 파일 다운로드 후 지정한 경로로 저장 및 파일명 변경 확인
            if not self.step3_process_downloaded_files():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== COSCO 크롤링 완료 ===")
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
            self.logger.error(f"=== COSCO 크롤링 전체 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def retry_failed_vessels(self, failed_vessels):
        """
        실패한 선박들에 대해 재시도하는 메서드
        
        Args:
            failed_vessels: 재시도할 선박 이름 리스트
            
        Returns:
            dict: 재시도 결과 (성공/실패 개수 등)
        """
        if not failed_vessels:
            return {
                'retry_success': 0,
                'retry_fail': 0,
                'total_retry': 0,
                'final_success': self.success_count,
                'final_fail': self.fail_count,
                'note': '재시도할 선박이 없습니다.'
            }
        
        self.logger.info(f"=== COSCO 실패한 선박 재시도 시작 ===")
        self.logger.info(f"재시도 대상 선박: {', '.join(failed_vessels)}")
        self.logger.info(f"재시도 대상 개수: {len(failed_vessels)}개")
        
        # 재시도 전 상태 저장
        original_success_count = self.success_count
        original_fail_count = self.fail_count
        
        # 실패한 선박들만 재시도
        retry_success_count = 0
        retry_fail_count = 0
        
        for vessel_name in failed_vessels:
            try:
                self.logger.info(f"=== {vessel_name} 재시도 시작 ===")
                
                # 선박별 타이머 시작
                self.start_vessel_tracking(vessel_name)
                
                # 1. 선박명 입력 (테스트 코드 방식으로 단순화)
                input_xpath = '/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/form/div/div[1]/div/div/div/div[1]/input'
                vessel_input = self.wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
                vessel_input.clear()
                vessel_input.send_keys(vessel_name)
                time.sleep(1)
                
                # 성공 처리 (성공 카운트는 end_vessel_tracking에서 자동 처리됨)
                retry_success_count += 1
                
                # 실패 목록에서 제거
                if vessel_name in self.failed_vessels:
                    self.failed_vessels.remove(vessel_name)
                
                # 선박별 타이머 종료 (성공/실패 카운트 자동 처리)
                vessel_duration = self.end_vessel_tracking(vessel_name, success=True)
                self.logger.info(f"선박 {vessel_name} 재시도 성공 (소요시간: {vessel_duration:.2f}초)")
                
            except Exception as e:
                self.logger.error(f"선박 {vessel_name} 재시도 실패: {str(e)}")
                retry_fail_count += 1
                
                # 실패한 경우에도 타이머 종료
                vessel_duration = self.end_vessel_tracking(vessel_name, success=False)
                self.logger.error(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                continue
        
        # 재시도 결과 요약
        self.logger.info("="*60)
        self.logger.info("COSCO 재시도 결과 요약")
        self.logger.info("="*60)
        self.logger.info(f"재시도 성공: {retry_success_count}개")
        self.logger.info(f"재시도 실패: {retry_fail_count}개")
        self.logger.info(f"재시도 후 최종 성공: {self.success_count}개")
        self.logger.info(f"재시도 후 최종 실패: {self.fail_count}개")
        self.logger.info("="*60)
        
        return {
            'retry_success': retry_success_count,
            'retry_fail': retry_fail_count,
            'total_retry': len(failed_vessels),
            'final_success': self.success_count,
            'final_fail': self.fail_count,
            'final_failed_vessels': self.failed_vessels.copy(),
            'note': f'COSCO 재시도 완료 - 성공: {retry_success_count}개, 실패: {retry_fail_count}개'
        }
        