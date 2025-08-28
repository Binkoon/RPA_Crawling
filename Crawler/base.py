### 해당 코드 역할 요약 ###
# 실제 역할:
# - 공통 기능 제공 (WebDriver, 로깅, 폴더 생성)
# - 모든 크롤러가 상속받는 부모 클래스
# - 기본 설정 및 초기화

# 하지 않는 것:
# - 데이터 파이프라인 직접 관리하지 않음
# - 크롤러 실행하지 않음

import os
import time
import logging
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from enum import Enum

class ErrorType(Enum):
    """에러 타입 분류"""
    NETWORK_ERROR = "network_error"           # 네트워크 오류 (재시도 가능)
    TIMEOUT_ERROR = "timeout_error"           # 타임아웃 오류 (재시도 가능)
    RATE_LIMIT_ERROR = "rate_limit_error"     # 요청 제한 오류 (대기 후 재시도)
    BLOCKED_ERROR = "blocked_error"           # 차단 오류 (재시도 불가)
    VALIDATION_ERROR = "validation_error"     # 검증 오류 (재시도 불가)
    SYSTEM_ERROR = "system_error"             # 시스템 오류 (재시도 불가)
    UNKNOWN_ERROR = "unknown_error"           # 알 수 없는 오류

class ParentsClass:
    def __init__(self, carrier_name):
        """크롤러 초기화"""
        self.carrier_name = carrier_name
        
        # 크롬 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080") # 해상도는 이거로 고정
        self.set_user_agent(chrome_options)  # 얘네 없으면 일부 선사는 차단함
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 크롤링 결과 추적
        self.success_count = 0
        self.fail_count = 0
        self.failed_vessels = []
        self.failed_reasons = {}
        self.vessel_name_list = []
        
        # 🆕 선박별 개별 시간 추적
        self.vessel_timings = {}
        self.vessel_start_times = {}
        
        # 폴더 생성 경로 설정
        self.base_download_dir = os.path.join(os.getcwd(), 'scheduleData')
        self.today_download_dir = os.path.join(self.base_download_dir, 
                                              datetime.now().strftime('%y%m%d'))
        
        # 로그 경로 설정
        self.log_base_dir = os.path.join(os.getcwd(), 'ErrorLog')
        self.today_log_dir = os.path.join(self.log_base_dir, 
                                         datetime.now().strftime('%Y-%m-%d'))
        
        # 폴더 생성
        self._safe_create_folder(self.base_download_dir)
        self._safe_create_folder(self.today_download_dir)
        self._safe_create_folder(self.log_base_dir)
        self._safe_create_folder(self.today_log_dir)
        
        # 로그 폴더 설정
        self.setup_log_folder()
        
        # 다운로드 경로 설정
        prefs = {"download.default_directory": self.today_download_dir}
        chrome_options.add_experimental_option("prefs", prefs)
        
        # WebDriver 초기화
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def setup_log_folder(self):
        """ErrorLog 폴더 구조 생성"""
        # ErrorLog 폴더 생성
        self.log_base_dir = os.path.join(os.getcwd(), "ErrorLog")
        self._safe_create_folder(self.log_base_dir)
        
        # 날짜별 폴더 생성 (YYYY-MM-DD 형식)
        self.today_log_folder = datetime.now().strftime("%Y-%m-%d")
        self.today_log_dir = os.path.join(self.log_base_dir, self.today_log_folder)
        self._safe_create_folder(self.today_log_dir)

    def setup_logging(self, carrier_name, has_error=False):
        """
        로깅 설정 - 에러가 발생한 경우에만 파일 로그 생성
        로거 인스턴스를 재사용하여 중복 생성을 방지합니다.
        
        Args:
            carrier_name: 선사명
            has_error: 에러 발생 여부 (True인 경우에만 파일 로그 생성)
        """
        # 로거 키 생성
        logger_key = f"{carrier_name}_{has_error}"
        
        # 이미 생성된 로거가 있으면 재사용
        if hasattr(self, '_loggers') and logger_key in self._loggers:
            return self._loggers[logger_key]
        
        # 핸들러 설정
        handlers = [logging.StreamHandler()]  # 콘솔 출력은 항상
        
        # 에러가 발생한 경우에만 파일 핸들러 추가
        if has_error:
            log_filename = f"{carrier_name.lower()}ErrorLog.txt"
            log_file_path = os.path.join(self.today_log_dir, log_filename)
            handlers.append(logging.FileHandler(log_file_path, encoding='utf-8'))
        
        # 로거 생성
        logger = logging.getLogger(f"{carrier_name}_{has_error}")
        logger.setLevel(logging.INFO)
        
        # 기존 핸들러 제거 (중복 방지)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 새 핸들러 추가
        for handler in handlers:
            logger.addHandler(handler)
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        for handler in handlers:
            handler.setFormatter(formatter)
        
        # 로거 인스턴스 저장 (재사용을 위해)
        if not hasattr(self, '_loggers'):
            self._loggers = {}
        self._loggers[logger_key] = logger
        
        return logger

    def _safe_create_folder(self, folder_path, max_retries=1, retry_delay=0.1):
        """
        안전한 폴더 생성 (재시도 로직 포함)
        
        Args:
            folder_path: 생성할 폴더 경로
            max_retries: 최대 재시도 횟수 (1회로 제한하여 차단 방지)
            retry_delay: 재시도 간 대기 시간 (초)
        """
        for attempt in range(max_retries + 1):  # +1은 최초 시도 포함
            try:
                # 폴더가 이미 존재하는지 확인
                if os.path.exists(folder_path):
                    return True
                
                # 폴더 생성 시도
                os.makedirs(folder_path, exist_ok=True)
                return True
                
            except (OSError, PermissionError) as e:
                if attempt < max_retries:
                    # 재시도 전 잠시 대기 (차단 방지를 위해 짧게)
                    time.sleep(retry_delay)
                    continue
                else:
                    # 최대 재시도 횟수 초과
                    logging.error(f"폴더 생성 실패: {folder_path}, 에러: {str(e)}")
                    raise e

    def Visit_Link(self, url):
        self.driver.get(url)

    def Close(self):
        self.driver.quit()

    def set_user_agent(self, chrome_options, user_agent=None):
        """
        크롬 옵션에 user-agent를 추가하는 메서드.
        user_agent를 지정하지 않으면 기본 최신 크롬 UA 사용.
        """
        if user_agent is None:
            user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        chrome_options.add_argument(f"--user-agent={user_agent}")

    def record_vessel_failure(self, vessel_name, reason, error_type=None, retryable=False):
        """선박 실패 기록 (향상된 버전)"""
        if vessel_name not in self.failed_vessels:
            self.failed_vessels.append(vessel_name)
            self.failed_reasons[vessel_name] = reason
        
        # 에러 타입에 따른 로그 레벨 결정
        if error_type == ErrorType.BLOCKED_ERROR:
            self.logger.error(f"선박 {vessel_name} 크롤링 차단: {reason}")
        else:
            self.logger.warning(f"선박 {vessel_name} 크롤링 실패 (재시도 가능): {reason}")

    def start_vessel_tracking(self, vessel_name):
        """🆕 선박별 크롤링 시작 시간 기록"""
        self.vessel_start_times[vessel_name] = datetime.now()
        if vessel_name not in self.vessel_name_list:
            self.vessel_name_list.append(vessel_name)

    def end_vessel_tracking(self, vessel_name, success=True):
        """🆕 선박별 크롤링 종료 시간 기록 및 소요시간 계산"""
        if vessel_name in self.vessel_start_times:
            start_time = self.vessel_start_times[vessel_name]
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 선박별 개별 소요시간 저장
            self.vessel_timings[vessel_name] = duration
            
            # 성공/실패 카운트 업데이트 (여기서만 카운트)
            if success:
                self.success_count += 1
                self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {duration:.2f}초)")
            else:
                self.fail_count += 1
                self.logger.warning(f"선박 {vessel_name} 크롤링 실패 (소요시간: {duration:.2f}초)")
            
            # 시작 시간 제거 (메모리 정리)
            del self.vessel_start_times[vessel_name]
        else:
            # 시작 시간이 없는 경우 기본값 설정
            self.vessel_timings[vessel_name] = 0.0
            if success:
                self.success_count += 1
            else:
                self.fail_count += 1

    def get_vessel_duration(self, vessel_name):
        """🆕 선박별 개별 소요시간 조회"""
        return self.vessel_timings.get(vessel_name, 0.0)
    
    def retry_failed_vessels(self, failed_vessels):
        """🆕 실패한 선박들 재시도 (기본 구현)"""
        if not failed_vessels:
            return None
        
        self.logger.info(f"=== {self.carrier_name} 실패한 선박 재시도 시작 ===")
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
        self.logger.info(f"{self.carrier_name} 재시도 결과 요약")
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
            'note': f'{self.carrier_name} 재시도 완료 - 성공: {retry_success_count}개, 실패: {retry_fail_count}개'
        }

    def get_save_path(self, carrier_name, vessel_name):
        """파일 저장 경로 생성"""
        filename = f"{carrier_name}_{vessel_name}.xlsx"
        return os.path.join(self.today_download_dir, filename)

    def smart_retry(self, func, max_retries=3, base_delay=1):
        """
        스마트 재시도 로직
        
        Args:
            func: 실행할 함수
            max_retries: 최대 재시도 횟수
            base_delay: 기본 대기 시간 (초)
            
        Returns:
            함수 실행 결과
        """
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                # 지수 백오프로 대기 시간 증가
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
                continue

    def analyze_error(self, error):
        """
        에러 분석 및 타입 분류
        
        Args:
            error: 발생한 에러 객체
            
        Returns:
            ErrorType: 에러 타입
        """
        error_str = str(error).lower()
        
        # 네트워크 관련 에러
        if any(keyword in error_str for keyword in ['connection', 'timeout', 'network']):
            return ErrorType.NETWORK_ERROR
        
        # 타임아웃 에러
        if any(keyword in error_str for keyword in ['timeout', 'timed out']):
            return ErrorType.TIMEOUT_ERROR
        
        # 요청 제한 에러
        if any(keyword in error_str for keyword in ['rate limit', 'too many requests', '429']):
            return ErrorType.RATE_LIMIT_ERROR
        
        # 차단 에러
        if any(keyword in error_str for keyword in ['blocked', 'forbidden', '403', 'access denied']):
            return ErrorType.BLOCKED_ERROR
        
        # 검증 에러
        if any(keyword in error_str for keyword in ['validation', 'invalid', 'bad request', '400']):
            return ErrorType.VALIDATION_ERROR
        
        # 시스템 에러
        if any(keyword in error_str for keyword in ['internal server error', '500', 'service unavailable']):
            return ErrorType.SYSTEM_ERROR
        
        return ErrorType.UNKNOWN_ERROR
