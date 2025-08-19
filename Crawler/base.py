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
from datetime import datetime

class ParentsClass:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080") # 해상도는 이거로 고정

        self.set_user_agent(chrome_options)  # 얘네 없으면 일부 선사는 차단함
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # ScheduleData 상위 폴더만 생성
        self.base_download_dir = os.path.join(os.getcwd(), "scheduleData")
        if not os.path.exists(self.base_download_dir):
            os.makedirs(self.base_download_dir)

        # 오늘 날짜 폴더명 (YYMMDD)
        self.today_folder = datetime.now().strftime("%y%m%d")
        self.today_download_dir = os.path.join(self.base_download_dir, self.today_folder)
        if not os.path.exists(self.today_download_dir):
            os.makedirs(self.today_download_dir)

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
        """ErrorLog 폴더 구조 생성"""
        # ErrorLog 폴더 생성
        self.log_base_dir = os.path.join(os.getcwd(), "ErrorLog")
        if not os.path.exists(self.log_base_dir):
            os.makedirs(self.log_base_dir)
        
        # 날짜별 폴더 생성 (YYYY-MM-DD 형식)
        self.today_log_folder = datetime.now().strftime("%Y-%m-%d")
        self.today_log_dir = os.path.join(self.log_base_dir, self.today_log_folder)
        if not os.path.exists(self.today_log_dir):
            os.makedirs(self.today_log_dir)

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

    def record_vessel_failure(self, vessel_name, reason):
        """선박 실패 기록"""
        if vessel_name not in self.failed_vessels:
            self.failed_vessels.append(vessel_name)
            self.failed_reasons[vessel_name] = reason
            self.fail_count += 1
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
        
        Args:
            failed_vessels: 재시도할 선박 이름 리스트
            
        Returns:
            dict: 재시도 결과 (성공/실패 개수 등)
        """
        self.logger.warning(f"기본 재시도 메서드가 호출되었습니다. {len(failed_vessels)}개 선박에 대한 재시도가 필요합니다.")
        self.logger.warning(f"재시도 대상 선박: {', '.join(failed_vessels)}")
        
        # 기본적으로는 재시도하지 않고 실패 상태 유지
        return {
            'retry_success': 0,
            'retry_fail': len(failed_vessels),
            'total_retry': len(failed_vessels),
            'final_success': self.success_count,
            'final_fail': self.fail_count,
            'note': '기본 재시도 메서드 - 구체적인 재시도 로직이 구현되지 않음'
        }
