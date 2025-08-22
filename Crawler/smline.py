# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/06/30 (완성)
# 선사 링크 : https://esvc.smlines.com/smline/CUP_HOM_3005.do?sessLocale=ko
# 선박 리스트 : ["SM JAKARTA"]
# 추가 정보 : 다운로드가 바로 되지 않고, "다른 이름으로 저장"으로 뜨는 경우는 아래 코드 사용.
# ++ 셀레니움의 Options를 사용할 것. 예시 코드는 아래에 있음. def __init__ 에 넣고 절대경로로 해야함.
"""
download_folder = r"C:\원하는\폴더\경로"  # 원하는 다운로드 경로로 변경

chrome_options = Options()
prefs = {
    "download.default_directory": download_folder,  # 다운로드 폴더 지정
    "download.prompt_for_download": False,          # 저장 위치 묻기 비활성화
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import logging
import traceback

from .base import ParentsClass
import time
import os

class SMLINE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__("SMLINE")
        self.carrier_name = "SML"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["SM JAKARTA"]
        
        # 크롤링 결과 추적
        self.success_count = 0
        self.fail_count = 0
        self.failed_vessels = []
        self.failed_reasons = {}

        # SMLINE은 저장할때, "다름이름으로 저장이 떠가지고 얘만 따로"
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        self.set_user_agent(chrome_options)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        prefs = {"download.default_directory": self.today_download_dir}
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver.quit()
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def setup_logging(self):
        """로깅 설정"""
        # 초기에는 에러가 없으므로 파일 로그 생성하지 않음
        self.logger = super().setup_logging(self.carrier_name, has_error=False)
        
    def setup_logging_with_error(self):
        """에러 발생 시 로깅 설정"""
        # 에러가 발생했으므로 파일 로그 생성
        self.logger = super().setup_logging(self.carrier_name, has_error=True)

    def step1_visit_website(self):
        """1단계: 선사 홈페이지 접속"""
        try:
            self.logger.info("=== 1단계: 선사 홈페이지 접속 시작 ===")
            
            # 0. 선사 접속
            self.Visit_Link("https://esvc.smlines.com/smline/CUP_HOM_3005.do?sessLocale=ko")
            driver = self.driver
            wait = self.wait

            # 1. input 찾기
            vessel_input = wait.until(EC.element_to_be_clickable((
                By.XPATH , '//*[@id="vslEngNm"]'
            )))
            vessel_input.click()
            
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
        """2단계: 지정된 선박별로 루핑 작업 시작"""
        try:
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
            driver = self.driver
            wait = self.wait

            # 2. 선박 넣기
            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_tracking(vessel_name)
                    
                    vessel_input = wait.until(EC.element_to_be_clickable((
                        By.XPATH , '//*[@id="vslEngNm"]'
                    )))
                    vessel_input.clear()
                    vessel_input.send_keys(vessel_name)
                    time.sleep(1)

                    vessel_select = wait.until(EC.element_to_be_clickable((
                        By.XPATH , '/html/body/ul/li'
                    )))
                    vessel_select.click()
                    time.sleep(1)

                    search_btn = wait.until(EC.element_to_be_clickable((
                        By.XPATH , '//*[@id="btnSearch"]'
                    )))
                    search_btn.click()
                    time.sleep(1)

                    download_btn = wait.until(EC.element_to_be_clickable((
                        By.XPATH , '//*[@id="btnDownload"]'
                    )))
                    download_btn.click()
                    time.sleep(1)

                    vessel_name = "SM JAKARTA"
                    old_path = os.path.join(self.today_download_dir, "Vessel Schedule.xls")
                    new_name = f"{self.carrier_name}_{vessel_name}.xls"
                    new_path = os.path.join(self.today_download_dir, new_name)

                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        self.logger.info(f"파일명 변경 완료: {new_path}")
                        # 성공 카운트는 end_vessel_tracking에서 자동 처리됨
                        
                        # 선박별 타이머 종료
                        self.end_vessel_tracking(vessel_name, success=True)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                        self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                    else:
                        self.logger.warning("다운로드 파일이 없습니다.")
                        self.record_step_failure(vessel_name, "데이터 크롤링", "다운로드 파일이 없음")
                        
                        # 실패한 경우에도 타이머 종료
                        self.end_vessel_tracking(vessel_name, success=True)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                        self.logger.warning(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패: {str(e)}")
                    # 실패한 경우에도 타이머 종료
                    self.end_vessel_tracking(vessel_name, success=True)
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

    def run(self):
        """메인 실행 함수"""
        try:
            self.logger.info("=== SMLINE 크롤링 시작 ===")
            
            # 1단계: 선사 홈페이지 접속
            if not self.step1_visit_website():
                return False
            
            # 2단계: 지정된 선박별로 루핑 작업 시작
            if not self.step2_crawl_vessel_data():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== SMLINE 크롤링 완료 ===")
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
            self.logger.error(f"=== SMLINE 크롤링 전체 실패 ===")
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
        
        self.logger.info(f"=== SMLINE 실패한 선박 재시도 시작 ===")
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
                vessel_input = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, '//*[@id="vslEngNm"]'
                )))
                vessel_input.clear()
                vessel_input.send_keys(vessel_name)
                time.sleep(1)
                
                # 2. 선박 선택
                vessel_select = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, '/html/body/ul/li'
                )))
                vessel_select.click()
                time.sleep(1)
                
                # 3. Search 버튼 클릭
                search_btn = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, '//*[@id="btnSearch"]'
                )))
                search_btn.click()
                time.sleep(1)
                
                # 4. Download 버튼 클릭
                download_btn = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH, '//*[@id="btnDownload"]'
                )))
                download_btn.click()
                time.sleep(1)
                
                # 5. 파일명 변경
                old_path = os.path.join(self.today_download_dir, "Vessel Schedule.xls")
                new_name = f"{self.carrier_name}_{vessel_name}.xls"
                new_path = os.path.join(self.today_download_dir, new_name)
                
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    self.logger.info(f"{vessel_name} 재시도 파일명 변경 완료: {new_path}")
                    
                    # 성공 처리
                    # 성공 카운트는 end_vessel_tracking에서 자동 처리됨
                    retry_success_count += 1
                    
                    # 실패 목록에서 제거
                    if vessel_name in self.failed_vessels:
                        self.failed_vessels.remove(vessel_name)
                    if vessel_name in self.failed_reasons:
                        del self.failed_reasons[vessel_name]
                    
                    self.end_vessel_tracking(vessel_name, success=True)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.info(f"선박 {vessel_name} 재시도 성공 (소요시간: {vessel_duration:.2f}초)")
                else:
                    self.logger.warning(f"{vessel_name} 재시도 시에도 다운로드 파일이 없음")
                    retry_fail_count += 1
                    self.end_vessel_tracking(vessel_name, success=True)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.warning(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                
            except Exception as e:
                self.logger.error(f"선박 {vessel_name} 재시도 실패: {str(e)}")
                retry_fail_count += 1
                
                # 실패한 경우에도 타이머 종료
                self.end_vessel_tracking(vessel_name, success=True)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                self.logger.error(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                continue
        
        # 재시도 결과 요약
        self.logger.info("="*60)
        self.logger.info("SMLINE 재시도 결과 요약")
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
            'note': f'SMLINE 재시도 완료 - 성공: {retry_success_count}개, 실패: {retry_fail_count}개'
        }  
