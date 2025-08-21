# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : 로깅 설정 공통 모듈

import os
import logging
from datetime import datetime

def setup_errorlog_folder():
    """ErrorLog 폴더 구조 생성"""
    log_base_dir = os.path.join(os.getcwd(), "ErrorLog")
    os.makedirs(log_base_dir, exist_ok=True)
    
    # 날짜별 폴더 생성 (YYYY-MM-DD 형식)
    today_log_folder = datetime.now().strftime("%Y-%m-%d")
    today_log_dir = os.path.join(log_base_dir, today_log_folder)
    os.makedirs(today_log_dir, exist_ok=True)
    
    return today_log_dir

def setup_main_logging():
    """메인 로깅 설정 (콘솔만)"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def get_today_log_dir():
    """오늘 날짜의 로그 디렉토리 경로 반환"""
    return setup_errorlog_folder()
