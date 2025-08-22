### 해당 코드 역할 요약 ###
# 실제 역할:
# - 공통 기능 제공 (WebDriver, 로깅, 폴더 생성)
# - 모든 크롤러가 상속받는 부모 클래스
# - 기본 설정 및 초기화

# 하지 않는 것:
# - 데이터 파이프라인 직접 관리하지 않음
# - 크롤러 실행하지 않음

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import logging
import os
import threading
import time
import requests
from datetime import datetime
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
    # 클래스 레벨 폴더 생성 잠금 (자원 경쟁 방지)
    _folder_creation_lock = threading.Lock()
    
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
        """ErrorLog 폴더 구조 생성 (자원 경쟁 방지)"""
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
        
        # 로거 인스턴스 저장 (재사용을 위해)
        if not hasattr(self, '_loggers'):
            self._loggers = {}
        self._loggers[logger_key] = logger
        
        return logger

    def analyze_error(self, error, context=""):
        """
        에러를 분석하여 타입과 재시도 가능 여부를 판단
        
        Args:
            error: 발생한 에러 객체
            context: 에러 발생 컨텍스트 (선박명, 단계명 등)
            
        Returns:
            dict: 에러 분석 결과
        """
        error_str = str(error).lower()
        error_type = ErrorType.UNKNOWN_ERROR
        retryable = False
        retry_delay = 0
        max_retries = 0
        
        # 네트워크 관련 에러
        if any(keyword in error_str for keyword in ['connection', 'timeout', 'network', 'dns']):
            error_type = ErrorType.NETWORK_ERROR
            retryable = True
            retry_delay = 5  # 5초 후 재시도
            max_retries = 2  # 최대 2회 재시도
            
        # 타임아웃 에러
        elif any(keyword in error_str for keyword in ['timeout', 'timed out', 'wait']):
            error_type = ErrorType.TIMEOUT_ERROR
            retryable = True
            retry_delay = 10  # 10초 후 재시도
            max_retries = 1  # 최대 1회 재시도
            
        # 요청 제한 에러
        elif any(keyword in error_str for keyword in ['rate limit', 'too many requests', '429', 'quota']):
            error_type = ErrorType.RATE_LIMIT_ERROR
            retryable = True
            retry_delay = 30  # 30초 후 재시도
            max_retries = 1  # 최대 1회 재시도
            
        # 차단 에러
        elif any(keyword in error_str for keyword in ['blocked', 'forbidden', '403', 'access denied']):
            error_type = ErrorType.BLOCKED_ERROR
            retryable = False
            retry_delay = 0
            max_retries = 0
            
        # 검증 에러
        elif any(keyword in error_str for keyword in ['validation', 'invalid', 'not found', '404']):
            error_type = ErrorType.VALIDATION_ERROR
            retryable = False
            retry_delay = 0
            max_retries = 0
            
        # 시스템 에러
        elif any(keyword in error_str for keyword in ['internal server', '500', 'service unavailable']):
            error_type = ErrorType.SYSTEM_ERROR
            retryable = True
            retry_delay = 60  # 1분 후 재시도
            max_retries = 1  # 최대 1회 재시도
        
        return {
            'error_type': error_type,
            'retryable': retryable,
            'retry_delay': retry_delay,
            'max_retries': max_retries,
            'context': context,
            'error_message': str(error)
        }

    def smart_retry(self, operation, operation_name="", max_retries=None, context=""):
        """
        에러 분석 기반 스마트 재시도 메서드
        
        Args:
            operation: 실행할 함수
            operation_name: 작업 이름 (로깅용)
            max_retries: 최대 재시도 횟수 (None이면 자동 결정)
            context: 컨텍스트 정보
            
        Returns:
            tuple: (성공 여부, 결과 또는 에러 정보)
        """
        last_error = None
        
        for attempt in range(10):  # 최대 10회 시도 (안전장치)
            try:
                result = operation()
                if attempt > 0:
                    self.logger.info(f"{operation_name} 재시도 성공 (시도 {attempt + 1}회)")
                return True, result
                
            except Exception as e:
                last_error = e
                error_analysis = self.analyze_error(e, context)
                
                # 재시도 불가능한 에러
                if not error_analysis['retryable']:
                    self.logger.error(f"{operation_name} 치명적 에러: {error_analysis['error_type'].value}")
                    self.logger.error(f"에러 메시지: {error_analysis['error_message']}")
                    return False, error_analysis
                
                # 최대 재시도 횟수 확인
                if max_retries is not None and attempt >= max_retries:
                    self.logger.error(f"{operation_name} 최대 재시도 횟수 초과: {max_retries}회")
                    return False, error_analysis
                
                # 자동 재시도 횟수 결정
                auto_max_retries = error_analysis['max_retries']
                if attempt >= auto_max_retries:
                    self.logger.error(f"{operation_name} 자동 재시도 횟수 초과: {auto_max_retries}회")
                    return False, error_analysis
                
                # 재시도 대기
                retry_delay = error_analysis['retry_delay']
                self.logger.warning(f"{operation_name} 재시도 {attempt + 1}회 (에러: {error_analysis['error_type'].value})")
                self.logger.info(f"{retry_delay}초 후 재시도...")
                time.sleep(retry_delay)
        
        # 최대 시도 횟수 초과 (안전장치)
        self.logger.error(f"{operation_name} 안전장치로 인한 재시도 중단 (최대 10회)")
        return False, {'error_type': ErrorType.SYSTEM_ERROR, 'retryable': False, 'context': context}

    def _safe_create_folder(self, folder_path, max_retries=1, retry_delay=0.1):
        """
        자원 경쟁을 방지하는 안전한 폴더 생성 메서드
        
        Args:
            folder_path: 생성할 폴더 경로
            max_retries: 최대 재시도 횟수 (1회로 제한하여 차단 방지)
            retry_delay: 재시도 간 대기 시간 (초)
        """
        # 스레드 안전한 폴더 생성
        with self._folder_creation_lock:
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
            self.fail_count += 1
        
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
            
            # 성공/실패 카운트 업데이트
            if success:
                self.success_count += 1
                self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {duration:.2f}초)")
            else:
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
        
        retry_success = 0
        retry_fail = 0
        
        for vessel_name in failed_vessels:
            try:
                # 재시도 시도
                success = self.retry_single_vessel(vessel_name)
                if success:
                    retry_success += 1
                    # 실패 목록에서 제거
                    if vessel_name in self.failed_vessels:
                        self.failed_vessels.remove(vessel_name)
                    if vessel_name in self.failed_reasons:
                        del self.failed_reasons[vessel_name]
                else:
                    retry_fail += 1
            except Exception as e:
                retry_fail += 1
                self.logger.error(f"선박 {vessel_name} 재시도 중 오류: {str(e)}")
        
        # 최종 결과 계산
        final_success = self.success_count
        final_fail = self.fail_count
        
        return {
            'retry_success': retry_success,
            'retry_fail': retry_fail,
            'final_success': final_success,
            'final_fail': final_fail,
            'final_failed_vessels': self.failed_vessels.copy(),
            'note': f"재시도 결과: 성공 {retry_success}개, 실패 {retry_fail}개"
        }
    
    def retry_single_vessel(self, vessel_name):
        """🆕 단일 선박 재시도 (기본 구현 - 하위 클래스에서 오버라이드)"""
        self.logger.warning(f"선박 {vessel_name} 재시도 메서드가 구현되지 않았습니다.")
        return False
    
    def get_save_path(self, carrier_name, vessel_name, ext="xlsx"):
        """
        저장 경로 생성 (예: scheduleData/250714/SITC_SITC DECHENG.xlsx)
        """
        # 파일명에 들어가면 안 되는 문자 제거
        safe_vessel = vessel_name.replace("/", "_").replace("\\", "_")
        safe_carrier = carrier_name.replace("/", "_").replace("\\", "_")
        filename = f"{safe_carrier}_{safe_vessel}.{ext}"
        return os.path.join(self.today_download_dir, filename)

    def get_error_statistics(self):
        """에러 통계 정보 반환"""
        error_stats = {
            'total_vessels': len(getattr(self, 'vessel_name_list', [])),
            'success_count': self.success_count,
            'fail_count': self.fail_count,
            'failed_vessels': self.failed_vessels.copy(),
            'failed_reasons': self.failed_reasons.copy(),
            'success_rate': 0.0
        }
        
        if error_stats['total_vessels'] > 0:
            error_stats['success_rate'] = (self.success_count / error_stats['total_vessels']) * 100
            
        return error_stats

    def log_error_summary(self):
        """에러 요약 로깅"""
        stats = self.get_error_statistics()
        
        self.logger.info("=" * 60)
        self.logger.info("크롤링 결과 요약")
        self.logger.info("=" * 60)
        self.logger.info(f"총 선박: {stats['total_vessels']}개")
        self.logger.info(f"성공: {stats['success_count']}개")
        self.logger.info(f"실패: {stats['fail_count']}개")
        self.logger.info(f"성공률: {stats['success_rate']:.1f}%")
        
        if stats['failed_vessels']:
            self.logger.info("실패한 선박:")
            for vessel in stats['failed_vessels']:
                reason = stats['failed_reasons'].get(vessel, "알 수 없는 오류")
                self.logger.info(f"  └─ {vessel}: {reason}")
        
        self.logger.info("=" * 60)
