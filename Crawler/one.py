# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/07/01 (완성)
# 선사 링크 : https://ecomm.one-line.com/one-ecom/public/vesselSchedule/search
# 선박 리스트 : ["ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG"]
# 추가 정보 : ONE은 PDF 파일을 다운로드 받음. 순차처리 + 순서 기반 파일명 매핑 사용.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import logging
import traceback

from .base import ParentsClass
import os
import pandas as pd
from datetime import datetime
import re

class ONE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__("ONE")  # carrier_name을 부모 클래스에 전달
        self.carrier_name = "ONE"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG", "ONE HAMBURG"]
        
        # 크롤링 결과 추적
        self.success_count = 0
        self.fail_count = 0
        self.failed_vessels = []
        self.failed_reasons = {}

    def setup_logging(self):
        """로깅 설정"""
        # 초기에는 에러가 없으므로 파일 로그 생성하지 않음
        self.logger = super().setup_logging(self.carrier_name, has_error=False)
        
    def setup_logging_with_error(self):
        """에러 발생 시 로깅 설정"""
        # 에러가 발생했으므로 파일 로그 생성
        self.logger = super().setup_logging(self.carrier_name, has_error=True)

    def step1_visit_and_download(self):
        """1단계: 선박별 접속 및 PDF 다운로드"""
        try:
            self.logger.info("=== 1단계: 선박별 접속 및 PDF 다운로드 시작 ===")
            
            driver = self.driver
            wait = self.wait
            
            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 접속 및 다운로드 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_tracking(vessel_name)
                    
                    # 1. 선박명 입력
                    vessel_input = wait.until(EC.presence_of_element_located((
                        By.XPATH, '//*[@id="vesselName"]'
                    )))
                    vessel_input.clear()
                    vessel_input.send_keys(vessel_name)
                    time.sleep(1)
                    
                    # 2. Search 버튼 클릭
                    search_btn = wait.until(EC.element_to_be_clickable((
                        By.XPATH, '//*[@id="searchBtn"]'
                    )))
                    search_btn.click()
                    time.sleep(2)
                    
                    # 3. PDF 다운로드 버튼 클릭
                    try:
                        download_pdf = wait.until(EC.element_to_be_clickable((
                            By.XPATH, '//*[@id="headlessui-dialog-:ra:"]/div[2]/div[3]/button[3]'
                        )))
                        driver.execute_script("arguments[0].scrollIntoView(true);", download_pdf)
                        driver.execute_script("arguments[0].click();", download_pdf)
                        self.logger.info("PDF 다운로드 버튼 클릭 완료")
                    except Exception as e:
                        self.logger.error(f"모달 또는 Download 버튼 클릭 중 오류 발생 ({vessel_name}): {e}")

                    # 4. 다운로드 완료 대기
                    time.sleep(3)  # PDF 다운로드 대기
                    
                    # 성공 카운트는 end_vessel_tracking에서 자동 처리됨
                    
                    # 선박별 타이머 종료
                    self.end_vessel_tracking(vessel_name, success=True)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.info(f"선박 {vessel_name} PDF 다운로드 완료 (소요시간: {vessel_duration:.2f}초)")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 접속 및 다운로드 실패: {str(e)}")
                    
                    # 실패한 경우에도 타이머 종료
                    self.end_vessel_tracking(vessel_name, success=False)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.error(f"선박 {vessel_name} 접속 및 다운로드 실패 (소요시간: {vessel_duration:.2f}초)")
                    
                    # 실패한 선박 기록
                    if vessel_name not in self.failed_vessels:
                        self.failed_vessels.append(vessel_name)
                        self.failed_reasons[vessel_name] = str(e)
                    
                    continue
            
            self.logger.info("=== 1단계: 선박별 접속 및 PDF 다운로드 완료 ===")
            self.logger.info(f"성공: {self.success_count}개, 실패: {self.fail_count}개")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 1단계: 선박별 접속 및 PDF 다운로드 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step2_process_downloaded_files(self):
        """2단계: 다운로드된 파일 처리 및 파일명 변경 (순서 기반 파일명 매핑)"""
        try:
            self.logger.info("=== 2단계: 파일 처리 및 파일명 변경 시작 ===")
            
            # 다운로드된 PDF 파일들을 순서대로 정렬
            pdf_files = [f for f in os.listdir(self.today_download_dir) if f.lower().endswith('.pdf')]
            pdf_files.sort()  # 파일명 순서대로 정렬
            
            # vessel_name_list와 1:1로 파일명 변경 (순서 기반 매핑)
            for i, vessel_name in enumerate(self.vessel_name_list):
                if i < len(pdf_files):
                    old_path = os.path.join(self.today_download_dir, pdf_files[i])
                    today_str = datetime.now().strftime("%y%m%d")
                    vessel_safe_name = vessel_name.replace(" ", "_").replace("(", "").replace(")", "")
                    new_filename = f"{self.carrier_name}_{vessel_safe_name}_{today_str}.pdf"
                    new_path = os.path.join(self.today_download_dir, new_filename)
                    os.rename(old_path, new_path)
                    self.logger.info(f"파일명 변경: {pdf_files[i]} → {new_filename}")
                else:
                    self.logger.warning(f"선박 {vessel_name}에 해당하는 파일을 찾을 수 없음")
            
            self.logger.info("=== 2단계: 파일 처리 및 파일명 변경 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 2단계: 파일 처리 및 파일명 변경 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def run(self):
        """메인 실행 함수"""
        try:
            self.logger.info("=== ONE 크롤링 시작 ===")
            
            # 1단계: 선박별 접속 및 PDF 다운로드
            if not self.step1_visit_and_download():
                return False
            
            # 2단계: 파일 처리 및 파일명 변경
            if not self.step2_process_downloaded_files():
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
        
        self.logger.info(f"=== ONE 실패한 선박 재시도 시작 ===")
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
                
                # 1. 선박명 입력
                vessel_input = self.wait.until(EC.presence_of_element_located((
                    By.XPATH, '//*[@id="vesselName"]'
                )))
                vessel_input.clear()
                vessel_input.send_keys(vessel_name)
                time.sleep(1)
                
                # 성공 처리 (end_vessel_tracking에서 자동 처리됨)
                retry_success_count += 1
                
                # 실패 목록에서 제거
                if vessel_name in self.failed_vessels:
                    self.failed_vessels.remove(vessel_name)
                if vessel_name in self.failed_reasons:
                    del self.failed_reasons[vessel_name]
                
                self.end_vessel_tracking(vessel_name, success=True)
                vessel_duration = self.get_vessel_duration(vessel_name)
                self.logger.info(f"선박 {vessel_name} 재시도 성공 (소요시간: {vessel_duration:.2f}초)")
                
            except Exception as e:
                self.logger.error(f"선박 {vessel_name} 재시도 실패: {str(e)}")
                retry_fail_count += 1
                
                # 실패한 경우에도 타이머 종료
                self.end_vessel_tracking(vessel_name, success=False)
                vessel_duration = self.get_vessel_duration(vessel_name)
                self.logger.error(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                continue
        
        # 재시도 결과 요약
        self.logger.info("="*60)
        self.logger.info("ONE 재시도 결과 요약")
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
            'note': f'ONE 재시도 완료 - 성공: {retry_success_count}개, 실패: {retry_fail_count}개'
        }