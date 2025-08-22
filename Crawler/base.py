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
    
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080") # 해상도는 이거로 고정

        self.set_user_agent(chrome_options)  # 얘네 없으면 일부 선사는 차단함
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # ScheduleData 상위 폴더만 생성 (자원 경쟁 방지)
        self.base_download_dir = os.path.join(os.getcwd(), "scheduleData")
        self._safe_create_folder(self.base_download_dir)

        # 오늘 날짜 폴더명 (YYMMDD)
        self.today_folder = datetime.now().strftime("%y%m%d")
        self.today_download_dir = os.path.join(self.base_download_dir, self.today_folder)
        self._safe_create_folder(self.today_download_dir)

        # Log 폴더 구조 생성
        self.setup_log_folder()

        prefs = {"download.default_directory": self.today_download_dir}
        chrome_options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        
        # 실패 추적을 위한 속성들
        self.success_count = 0
        self.fail_count = 0
        self.failed_vessels = []
        self.failed_reasons = {}
        
        # 선박별 소요시간 추적
        self.vessel_durations = {}

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
            
        # 에러 타입별 로깅
        if error_type:
            if error_type in [ErrorType.BLOCKED_ERROR, ErrorType.VALIDATION_ERROR]:
                self.logger.error(f"선박 {vessel_name} 치명적 실패: {reason} (타입: {error_type.value})")
            elif error_type in [ErrorType.NETWORK_ERROR, ErrorType.TIMEOUT_ERROR]:
                self.logger.warning(f"선박 {vessel_name} 일시적 실패: {reason} (타입: {error_type.value}, 재시도: {'가능' if retryable else '불가'})")
            else:
                self.logger.warning(f"선박 {vessel_name} 실패: {reason} (타입: {error_type.value})")
        else:
            self.logger.warning(f"선박 {vessel_name} 실패: {reason}")
    
    def record_vessel_success(self, vessel_name):
        """선박 성공 기록"""
        self.success_count += 1
        self.logger.info(f"선박 {vessel_name} 성공")
    
    def record_step_failure(self, vessel_name, step_name, reason):
        """특정 단계에서의 실패 기록"""
        detailed_reason = f"{step_name} 실패: {reason}"
        self.record_vessel_failure(vessel_name, detailed_reason)
    
    def start_vessel_timer(self, vessel_name):
        """선박별 타이머 시작"""
        self.vessel_durations[vessel_name] = {'start': datetime.now()}
    
    def end_vessel_timer(self, vessel_name):
        """선박별 타이머 종료 및 소요시간 계산"""
        if vessel_name in self.vessel_durations and 'start' in self.vessel_durations[vessel_name]:
            start_time = self.vessel_durations[vessel_name]['start']
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self.vessel_durations[vessel_name]['duration'] = duration
            return duration
        return 0
    
    def get_vessel_duration(self, vessel_name):
        """선박별 소요시간 반환"""
        if vessel_name in self.vessel_durations and 'duration' in self.vessel_durations[vessel_name]:
            return self.vessel_durations[vessel_name]['duration']
        return 0
    
    def get_save_path(self, carrier_name, vessel_name, ext="xlsx"):
        """
        저장 경로 생성 (예: scheduleData/250714/SITC_SITC DECHENG.xlsx)
        """
        # 파일명에 들어가면 안 되는 문자 제거
        safe_vessel = vessel_name.replace("/", "_").replace("\\", "_")
        safe_carrier = carrier_name.replace("/", "_").replace("\\", "_")
        filename = f"{safe_carrier}_{safe_vessel}.{ext}"
        return os.path.join(self.today_download_dir, filename)
    
    def retry_failed_vessels(self, failed_vessels):
        """
        실패한 선박들에 대해 재시도하는 기본 메서드
        자식 클래스에서 오버라이드하여 구체적인 재시도 로직 구현
        
        ⚠️ 중요: 재시도는 1회만 허용 (잦은 호출로 인한 차단 방지)
        
        Args:
            failed_vessels: 재시도할 선박 이름 리스트
            
        Returns:
            dict: 재시도 결과 (성공/실패 개수 등)
        """
        self.logger.warning(f"기본 재시도 메서드가 호출되었습니다. {len(failed_vessels)}개 선박에 대한 재시도가 필요합니다.")
        self.logger.warning(f"재시도 대상 선박: {', '.join(failed_vessels)}")
        self.logger.warning("⚠️ 재시도는 1회만 허용됩니다 (차단 방지)")
        
        # 기본적으로는 재시도하지 않고 실패 상태 유지
        return {
            'retry_success': 0,
            'retry_fail': len(failed_vessels),
            'total_retry': len(failed_vessels),
            'final_success': self.success_count,
            'final_fail': self.fail_count,
            'note': '기본 재시도 메서드 - 구체적인 재시도 로직이 구현되지 않음 (재시도 1회 제한)'
        }

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
