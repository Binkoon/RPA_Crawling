# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/07/01 (완성)
# 선사 링크 : https://ecomm.one-line.com/one-ecom/schedule/vessel-schedule?vslCdParam=RCMT&vslEngNmParam=MARIA+C+%28RCMT%29&f_cmd=   MARIA C
# 선사 링크 : https://ecomm.one-line.com/one-ecom/schedule/vessel-schedule?vslCdParam=RSCT&vslEngNmParam=ONE+REASSURANCE+%28RSCT%29&f_cmd=  ONE REASSURANCE
# https://ecomm.one-line.com/one-ecom/schedule/vessel-schedule?vslCdParam=TSCT&vslEngNmParam=ST+SUCCESS+%28TSCT%29&f_cmd=  ST SUCCESS
# 선사 링크 : https://ecomm.one-line.com/one-ecom/schedule/vessel-schedule?vslCdParam=OMJT&vslEngNmParam=ONE+MAJESTY+%28OMJT%29&f_cmd=  ONE MAJESTY    
# 선박 리스트 : ["MARIA C", "ONE REASSURANCE", "ST SUCCESS", "ONE MAJESTY"]
# 추가 정보 : ONE은 PDF 파일을 다운로드 받음. 순차처리 + 순서 기반 파일명 매핑 사용.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import logging
import traceback
import re

from .base import ParentsClass
import os
import pandas as pd
from datetime import datetime

class ONE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__("ONE")  # carrier_name을 부모 클래스에 전달
        self.carrier_name = "ONE"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트 (현재 one.py 유지)
        self.vessel_name_list = ["MARIA C", "ONE REASSURANCE", "ST SUCCESS", "ONE MAJESTY"]
        
        # 선박별 파라미터 매핑 (동적 URL 생성용)
        self.vessel_params = {
            "MARIA C": {"vslCdParam": "RCMT", "vslEngNmParam": "MARIA+C+%28RCMT%29"},
            "ONE REASSURANCE": {"vslCdParam": "RSCT", "vslEngNmParam": "ONE+REASSURANCE+%28RSCT%29"},
            "ST SUCCESS": {"vslCdParam": "TSCT", "vslEngNmParam": "ST+SUCCESS+%28TSCT%29"},
            "ONE MAJESTY": {"vslCdParam": "OMJT", "vslEngNmParam": "ONE+MAJESTY+%28OMJT%29"}
        }
        
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
        """1단계: 선박별 직접 URL 접속 및 PDF 다운로드"""
        try:
            self.logger.info("=== 1단계: 선박별 직접 URL 접속 및 PDF 다운로드 시작 ===")
            
            driver = self.driver
            wait = self.wait
            
            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 접속 및 다운로드 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_tracking(vessel_name)
                    
                    # 1. 선박별 URL로 직접 접속
                    params = self.vessel_params.get(vessel_name)
                    if not params:
                        self.logger.error(f"선박 {vessel_name}에 대한 파라미터를 찾을 수 없음")
                        continue
                    
                    # 동적 URL 생성
                    vessel_url = f"https://ecomm.one-line.com/one-ecom/schedule/vessel-schedule?vslCdParam={params['vslCdParam']}&vslEngNmParam={params['vslEngNmParam']}&f_cmd="
                    self.Visit_Link(vessel_url)
                    time.sleep(7)  # 초기 로딩 대기 (3초 → 7초로 증가)
                    
                    # 2. PDF 다운로드 버튼 클릭
                    try:
                        # 1단계: 다운로드 버튼 클릭 (모달팝업 열림)
                        download_btn = wait.until(EC.element_to_be_clickable((
                            By.XPATH, '//*[@id="__next"]/main/div[2]/div[2]/div[7]/div[1]/div[3]/div/div[2]/button'
                        ))) # //*[@id="__next"]/main/div[2]/div[2]/div[7]/div[1]/div[3]/div/div[2]/button  -> 이게 첫번째 다운로드 버튼임.
                        driver.execute_script("arguments[0].scrollIntoView(true);", download_btn)
                        driver.execute_script("arguments[0].click();", download_btn)
                        self.logger.info(f"선박 {vessel_name} 다운로드 버튼 클릭 완료 (모달팝업 열림)")
                        time.sleep(4)  # 모달팝업 로딩 대기 (4초 유지)
                        
                        # 2단계: 모달 팝업 대기 및 PDF 다운로드 설정
                        try:
                            # 모달이 나타날 때까지 대기
                            modal = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="headlessui-dialog-:ra:"]')))
                            self.logger.info(f"모달 팝업 감지됨 ({vessel_name})")
                            
                            # PDF 라디오 버튼 클릭
                            pdf_radio = wait.until(EC.element_to_be_clickable((
                                By.XPATH, '//*[@id="headlessui-dialog-:ra:"]/div[2]/div[2]/div[2]/label/div'
                            ))) # //*[@id="headlessui-dialog-:ra:"]/div[2]/div[2]/div[2]/label/div
                            driver.execute_script("arguments[0].click();", pdf_radio)
                            self.logger.info("PDF 다운로드 옵션 선택 완료")
                            time.sleep(2)  # 선택 반영 대기 (2초 유지)
                            
                            # 추가: 다운로드 범위 설정 (선택적)
                            try:
                                # 현재 페이지만 다운로드 옵션이 있다면 선택
                                current_page_option = driver.find_elements(By.XPATH, '//*[@id="headlessui-dialog-:ra:"]//label[contains(text(), "Current") or contains(text(), "현재")]')
                                if current_page_option:
                                    driver.execute_script("arguments[0].click();", current_page_option[0])
                                    self.logger.info("현재 페이지만 다운로드 옵션 선택")
                                    time.sleep(1)
                            except Exception as e:
                                self.logger.info("현재 페이지 옵션을 찾을 수 없음, 기본 설정 사용")
                            
                            # 3단계: PDF 다운로드 버튼 클릭
                            download_pdf = wait.until(EC.element_to_be_clickable((
                                By.XPATH, '//*[@id="headlessui-dialog-:ra:"]/div[2]/div[3]/button[3]'
                            ))) # //*[@id="headlessui-dialog-:ra:"]/div[2]/div[3]/button[3]  -> pdf 다운로드 버튼임.
                            driver.execute_script("arguments[0].scrollIntoView(true);", download_pdf)
                            driver.execute_script("arguments[0].click();", download_pdf)
                            self.logger.info(f"선박 {vessel_name} PDF 다운로드 버튼 클릭 완료")
                            
                        except Exception as e:
                            self.logger.error(f"모달 또는 Download 버튼 클릭 중 오류 발생 ({vessel_name}): {e}")
                            raise e
                        
                    except Exception as e:
                        self.logger.error(f"PDF 다운로드 중 오류 발생 ({vessel_name}): {e}")
                        self.fail_count += 1
                        self.end_vessel_tracking(vessel_name, success=False)
                        continue

                    # 3. 다운로드 완료 대기 (one_test.py 방식으로 변경)
                    self.logger.info(f"PDF 다운로드 대기 중... ({vessel_name})")
                    time.sleep(15)  # 다운로드 대기 (wait_for_download → 15초로 변경)
                    
                    # 4. 파일명 즉시 변경 (ONE 방식으로 추가)
                    if self.rename_downloaded_file(vessel_name):
                        self.logger.info(f"선박 {vessel_name} 파일명 즉시 변경 성공")
                    else:
                        self.logger.warning(f"선박 {vessel_name} 파일명 즉시 변경 실패")
                    
                    # 다음 선박 처리 전 충분한 대기 (서버 부하 방지)
                    time.sleep(5)  # 5초 유지
                    
                    # 성공 처리
                    self.success_count += 1
                    
                    # 선박별 타이머 종료
                    self.end_vessel_tracking(vessel_name, success=True)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패: {str(e)}")
                    # 실패한 선박 기록
                    self.record_vessel_failure(vessel_name, str(e))
                    
                    # 실패한 경우에도 타이머 종료
                    self.end_vessel_tracking(vessel_name, success=False)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                    
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
        """2단계: 파일명 변경 확인 (즉시 변경 방식으로 변경)"""
        try:
            self.logger.info("=== 2단계: 파일명 변경 확인 시작 ===")
            
            # 파일명 변경이 성공적으로 완료되었는지 확인
            pdf_files = [f for f in os.listdir(self.today_download_dir) if f.lower().endswith('.pdf')]
            
            # 파일명 변경 확인 및 로깅
            for vessel_name in self.vessel_name_list:
                vessel_safe_name = vessel_name.replace(" ", "_").replace("(", "").replace(")", "")
                today_str = datetime.now().strftime("%y%m%d")
                expected_filename_pattern = f"{self.carrier_name}_{vessel_safe_name}_{today_str}"
                
                # 패턴에 맞는 파일 찾기
                matching_files = [f for f in pdf_files if f.startswith(expected_filename_pattern)]
                
                if matching_files:
                    self.logger.info(f"선박 {vessel_name}: 파일명 변경 확인됨 - {matching_files[0]}")
                else:
                    self.logger.warning(f"선박 {vessel_name}: 파일명 변경 확인 실패 - {expected_filename_pattern} 패턴의 파일이 없음")
            
            self.logger.info("=== 2단계: 파일명 변경 확인 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 2단계: 파일명 변경 확인 실패 ===")
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
                
                # 1. 선박별 URL로 직접 접속
                params = self.vessel_params.get(vessel_name)
                if not params:
                    self.logger.error(f"선박 {vessel_name}에 대한 파라미터를 찾을 수 없음")
                    retry_fail_count += 1
                    continue
                
                # 동적 URL 생성
                vessel_url = f"https://ecomm.one-line.com/one-ecom/schedule/vessel-schedule?vslCdParam={params['vslCdParam']}&vslEngNmParam={params['vslEngNmParam']}&f_cmd="
                self.Visit_Link(vessel_url)
                time.sleep(7)  # 페이지 로딩 대기 (3초 → 7초로 증가)
                
                # 2. PDF 다운로드 버튼 클릭
                try:
                    # 1단계: 다운로드 버튼 클릭 (모달팝업 열림)
                    download_btn = self.wait.until(EC.element_to_be_clickable((
                        By.XPATH, '//*[@id="__next"]/main/div[2]/div[2]/div[7]/div[1]/div[3]/div/div[2]/button'
                    )))
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", download_btn)
                    self.driver.execute_script("arguments[0].click();", download_btn)
                    self.logger.info(f"선박 {vessel_name} 다운로드 버튼 클릭 완료 (모달팝업 열림)")
                    time.sleep(4)  # 모달팝업 로딩 대기
                    
                    # 2단계: 모달 팝업 대기 및 PDF 다운로드 설정
                    try:
                        # 모달이 나타날 때까지 대기
                        modal = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="headlessui-dialog-:ra:"]')))
                        self.logger.info(f"모달 팝업 감지됨 ({vessel_name})")
                        
                        # PDF 라디오 버튼 클릭
                        pdf_radio = self.wait.until(EC.element_to_be_clickable((
                            By.XPATH, '//*[@id="headlessui-dialog-:ra:"]/div[2]/div[2]/div[2]/label/div'
                        )))
                        self.driver.execute_script("arguments[0].click();", pdf_radio)
                        self.logger.info("PDF 다운로드 옵션 선택 완료")
                        time.sleep(2)  # 선택 반영 대기
                        
                        # 3단계: PDF 다운로드 버튼 클릭
                        download_pdf = self.wait.until(EC.element_to_be_clickable((
                            By.XPATH, '//*[@id="headlessui-dialog-:ra:"]/div[2]/div[3]/button[3]'
                        )))
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", download_pdf)
                        self.driver.execute_script("arguments[0].click();", download_pdf)
                        self.logger.info(f"선박 {vessel_name} PDF 다운로드 버튼 클릭 완료 (재시도)")
                        
                    except Exception as e:
                        self.logger.error(f"모달 또는 Download 버튼 클릭 중 오류 발생 ({vessel_name}, 재시도): {e}")
                        retry_fail_count += 1
                        self.end_vessel_tracking(vessel_name, success=False)
                        continue
                        
                except Exception as e:
                    self.logger.error(f"PDF 다운로드 버튼 클릭 중 오류 발생 ({vessel_name}, 재시도): {e}")
                    retry_fail_count += 1
                    self.end_vessel_tracking(vessel_name, success=False)
                    continue
                
                # 3. 다운로드 완료 대기 (one_test.py 방식으로 변경)
                self.logger.info(f"PDF 다운로드 대기 중... ({vessel_name})")
                time.sleep(15)  # 다운로드 대기 (wait_for_download → 15초로 변경)
                
                # 4. 파일명 즉시 변경 (ONE 방식으로 추가)
                if self.rename_downloaded_file(vessel_name):
                    self.logger.info(f"선박 {vessel_name} 파일명 즉시 변경 성공 (재시도)")
                else:
                    self.logger.warning(f"선박 {vessel_name} 파일명 즉시 변경 실패 (재시도)")
                
                # 다음 선박 처리 전 충분한 대기 (서버 부하 방지)
                time.sleep(5)  # 3초 → 5초로 증가
                
                # 성공 처리
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

    def rename_downloaded_file(self, vessel_name, timeout=30):
        """다운로드된 파일을 선박명으로 즉시 변경"""
        try:
            start_time = time.time()
            renamed = False
            
            while time.time() - start_time < timeout:
                # 다운로드 디렉토리에서 가장 최근 PDF 파일 찾기
                pdf_files = [f for f in os.listdir(self.today_download_dir) if f.lower().endswith('.pdf')]
                
                if pdf_files:
                    # 가장 최근 파일 선택 (수정 시간 기준)
                    latest_pdf = max(pdf_files, key=lambda f: os.path.getmtime(os.path.join(self.today_download_dir, f)))
                    latest_pdf_path = os.path.join(self.today_download_dir, latest_pdf)
                    
                    # 파일명이 이미 변경되었는지 확인
                    if latest_pdf.startswith(f"{self.carrier_name}_{vessel_name}"):
                        self.logger.info(f"선박 {vessel_name}: 파일명이 이미 올바르게 설정됨")
                        return True
                    
                    # 파일이 아직 다운로드 중인지 확인 (.crdownload, .tmp 파일)
                    if latest_pdf.endswith('.crdownload') or latest_pdf.endswith('.tmp'):
                        time.sleep(1)
                        continue
                    
                    # 새 파일명 생성 (ONE의 파일명 규칙에 맞춤)
                    today_str = datetime.now().strftime("%y%m%d")
                    vessel_safe_name = vessel_name.replace(" ", "_").replace("(", "").replace(")", "")
                    new_filename = f"{self.carrier_name}_{vessel_safe_name}_{today_str}.pdf"
                    new_filepath = os.path.join(self.today_download_dir, new_filename)
                    
                    # 기존 파일이 있으면 넘버링 처리
                    base_name = new_filename.replace(".pdf", "")
                    counter = 1
                    final_filename = new_filename
                    
                    while os.path.exists(os.path.join(self.today_download_dir, final_filename)):
                        final_filename = f"{base_name}_{counter}.pdf"
                        counter += 1
                    
                    final_filepath = os.path.join(self.today_download_dir, final_filename)
                    
                    # 파일명 변경
                    try:
                        os.rename(latest_pdf_path, final_filepath)
                        self.logger.info(f"선박 {vessel_name}: 파일명 즉시 변경 완료 - {latest_pdf} → {final_filename}")
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
                self.logger.warning(f"선박 {vessel_name}: 파일명 즉시 변경 실패 - PDF 파일을 찾을 수 없음")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"선박 {vessel_name}: 파일명 즉시 변경 중 오류 발생 - {str(e)}")
            return False