# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/01/27
# 역할 : 폴더 생성 및 관리를 담당하는 클래스

import os
import time
from datetime import datetime

class FolderManager:
    """폴더 생성 및 관리를 담당하는 클래스"""
    
    def __init__(self):
        self.base_download_dir = os.path.join(os.getcwd(), 'scheduleData')
        self.log_base_dir = os.path.join(os.getcwd(), 'ErrorLog')
        self.today_download_dir = None
        self.today_log_dir = None
    
    def setup_today_directories(self):
        """오늘 날짜의 디렉토리 설정"""
        today_date = datetime.now()
        
        # 다운로드 디렉토리 (YYMMDD 형식)
        self.today_download_dir = os.path.join(
            self.base_download_dir, 
            today_date.strftime('%y%m%d')
        )
        
        # 로그 디렉토리 (YYYY-MM-DD 형식)
        self.today_log_dir = os.path.join(
            self.log_base_dir, 
            today_date.strftime('%Y-%m-%d')
        )
    
    def create_all_directories(self):
        """모든 필요한 디렉토리 생성"""
        self.setup_today_directories()
        
        directories = [
            self.base_download_dir,
            self.today_download_dir,
            self.log_base_dir,
            self.today_log_dir
        ]
        
        for directory in directories:
            self._safe_create_folder(directory)
    
    def _safe_create_folder(self, folder_path: str, max_retries: int = 1, retry_delay: float = 0.1):
        """
        안전한 폴더 생성 (재시도 로직 포함)
        
        Args:
            folder_path: 생성할 폴더 경로
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 간 대기 시간 (초)
        """
        for attempt in range(max_retries + 1):
            try:
                if os.path.exists(folder_path):
                    return True
                
                os.makedirs(folder_path, exist_ok=True)
                return True
                
            except (OSError, PermissionError) as e:
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise e
    
    def get_download_dir(self) -> str:
        """다운로드 디렉토리 반환"""
        return self.today_download_dir
    
    def get_log_dir(self) -> str:
        """로그 디렉토리 반환"""
        return self.today_log_dir
    
    def get_save_path(self, carrier_name: str, vessel_name: str) -> str:
        """파일 저장 경로 생성"""
        filename = f"{carrier_name}_{vessel_name}.xlsx"
        return os.path.join(self.today_download_dir, filename)
