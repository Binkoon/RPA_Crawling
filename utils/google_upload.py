# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : 구글 드라이브 업로드 공통 모듈

import os
import sys
import traceback
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

ERRORLOG_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_ERRORLOG_FOLDER_ID')
if not ERRORLOG_DRIVE_FOLDER_ID:
    raise ValueError("GOOGLE_DRIVE_ERRORLOG_FOLDER_ID 환경 변수가 설정되지 않았습니다.")

def get_google_drive_service():
    """구글 드라이브 서비스 생성"""
    sys.path.append(os.path.join(os.getcwd(), 'Google'))
    from Google.upload_to_drive_oauth import get_drive_service
    return get_drive_service()

def upload_errorlog_to_drive(logger):
    """에러로그를 구글드라이브에 업로드 (오늘 날짜의 _log.xlsx 파일만)"""
    logger.info("=== 에러로그 구글드라이브 업로드 시작 ===")
    
    try:
        # 드라이브 서비스 생성
        service = get_google_drive_service()
        logger.info(" 구글 드라이브 서비스 연결 성공")
        
        # 오늘 날짜의 에러로그 파일 찾기
        today = datetime.now()
        today_folder = today.strftime('%Y-%m-%d')
        today_log_file = f"{today.strftime('%Y%m%d')}_log.xlsx"
        
        # 오늘 날짜 폴더 경로
        today_folder_path = os.path.join(os.getcwd(), "ErrorLog", today_folder)
        today_log_path = os.path.join(today_folder_path, today_log_file)
        
        # 오늘 날짜의 로그 파일이 존재하는지 확인
        if not os.path.exists(today_log_path):
            logger.warning(f" 오늘 날짜({today_folder})의 로그 파일이 없습니다: {today_log_file}")
            return {
                'success': False,
                'message': f'오늘 날짜({today_folder})의 로그 파일이 없음: {today_log_file}',
                'uploaded_files': [],
                'failed_files': []
            }
        
        logger.info(f" 오늘 날짜({today_folder})의 로그 파일 발견: {today_log_file}")
        
        # 지정된 폴더 ID에 바로 업로드
        target_folder_id = ERRORLOG_DRIVE_FOLDER_ID
        logger.info(f" 지정된 폴더에 바로 업로드: {target_folder_id}")
        
        # 파일 업로드
        from Google.upload_to_drive_oauth import upload_file_to_drive
        
        file_size = os.path.getsize(today_log_path)
        file_modified = datetime.fromtimestamp(os.path.getmtime(today_log_path))
        
        upload_file_to_drive(service, today_log_path, target_folder_id)
        
        logger.info(f" {today_log_file} 업로드 완료")
        
        return {
            'success': True,
            'total_files': 1,
            'uploaded_files': [{
                'filename': today_log_file,
                'file_id': 'N/A',
                'size': file_size,
                'modified': file_modified
            }],
            'failed_files': [],
            'success_count': 1,
            'fail_count': 0
        }
        
    except Exception as e:
        error_msg = f"에러로그 업로드 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        logger.error(f"상세 에러: {traceback.format_exc()}")
        return {
            'success': False,
            'message': error_msg,
            'uploaded_files': [],
            'failed_files': []
        }

def run_main_upload():
    """메인 구글 드라이브 업로드 실행"""
    try:
        sys.path.append(os.path.join(os.getcwd(), 'Google'))
        from Google.upload_to_drive_oauth import main as upload_to_drive_main
        return upload_to_drive_main()
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'uploaded_files': [],
            'failed_files': []
        }
