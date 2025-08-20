### 에러로그 자동 업로드 및 정리 테스트 스크립트 ###
# 목적:
# - 에러로그를 구글드라이브에 자동 업로드
# - 30일 기준으로 오래된 에러로그 정리
# - 기존 스케줄 파일 업로드 로직과 동일한 방식 사용

import os
import sys
import datetime
import logging
import traceback
import shutil
from pathlib import Path

# Google 폴더의 업로드 스크립트 import
sys.path.append(os.path.join(os.getcwd(), 'Google'))
from Google.upload_to_drive_oauth import get_drive_service, find_folder_in_drive, create_folder_in_drive, upload_file_to_drive

# 에러로그 구글드라이브 폴더 ID
ERRORLOG_DRIVE_FOLDER_ID = '1t3P2oofZKnSrVMmDS6-YQcwuZC6PdCz5'

# ErrorLog 폴더 경로
ERRORLOG_BASE_DIR = os.path.join(os.getcwd(), "ErrorLog")

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def get_errorlog_folders():
    """ErrorLog 폴더 내의 모든 날짜별 폴더 목록 반환"""
    if not os.path.exists(ERRORLOG_BASE_DIR):
        return []
    
    folders = []
    for item in os.listdir(ERRORLOG_BASE_DIR):
        item_path = os.path.join(ERRORLOG_BASE_DIR, item)
        if os.path.isdir(item_path):
            # YYYY-MM-DD 형식인지 확인
            try:
                datetime.datetime.strptime(item, '%Y-%m-%d')
                folders.append(item)
            except ValueError:
                continue
    
    return sorted(folders)

def get_files_in_errorlog_folder(folder_name):
    """특정 에러로그 폴더 내의 파일 목록 반환"""
    folder_path = os.path.join(ERRORLOG_BASE_DIR, folder_name)
    if not os.path.exists(folder_path):
        return []
    
    files = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            files.append({
                'name': filename,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'modified': datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            })
    
    return files

def upload_errorlog_to_drive(logger):
    """에러로그를 구글드라이브에 업로드 (오늘 날짜의 _log.xlsx 파일만)"""
    logger.info("=== 에러로그 구글드라이브 업로드 시작 ===")
    
    try:
        # 드라이브 서비스 생성
        service = get_drive_service()
        logger.info("✅ 구글 드라이브 서비스 연결 성공")
        
        # 오늘 날짜의 에러로그 파일 찾기
        today = datetime.datetime.now()
        today_folder = today.strftime('%Y-%m-%d')
        today_log_file = f"{today.strftime('%Y%m%d')}_log.xlsx"
        
        # 오늘 날짜 폴더 경로
        today_folder_path = os.path.join(ERRORLOG_BASE_DIR, today_folder)
        today_log_path = os.path.join(today_folder_path, today_log_file)
        
        # 오늘 날짜의 로그 파일이 존재하는지 확인
        if not os.path.exists(today_log_path):
            logger.warning(f"⚠️ 오늘 날짜({today_folder})의 로그 파일이 없습니다: {today_log_file}")
            return {
                'success': False,
                'message': f'오늘 날짜({today_folder})의 로그 파일이 없음: {today_log_file}',
                'uploaded_files': [],
                'failed_files': []
            }
        
        logger.info(f"📁 오늘 날짜({today_folder})의 로그 파일 발견: {today_log_file}")
        
        # 지정된 폴더 ID에 바로 업로드 (ErrorLog 폴더 생성 불필요)
        target_folder_id = ERRORLOG_DRIVE_FOLDER_ID
        logger.info(f"📁 지정된 폴더에 바로 업로드: {target_folder_id}")
        
        # 오늘 날짜의 로그 파일만 업로드
        uploaded_files = []
        failed_files = []
        
        try:
            # 파일 정보 가져오기
            file_size = os.path.getsize(today_log_path)
            file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(today_log_path))
            
            # 파일 업로드
            upload_file_to_drive(service, today_log_path, target_folder_id)
            uploaded_files.append({
                'filename': today_log_file,
                'file_id': 'N/A',
                'size': file_size,
                'modified': file_modified
            })
            
            logger.info(f"✅ {today_log_file} 업로드 완료")
            
        except Exception as e:
            failed_files.append({
                'filename': today_log_file,
                'error': str(e)
            })
            logger.error(f"❌ {today_log_file} 업로드 실패: {str(e)}")
        
        # 최종 결과 출력
        success_count = len(uploaded_files)
        fail_count = len(failed_files)
        total_files = success_count + fail_count
        
        logger.info("="*60)
        logger.info("📊 에러로그 업로드 결과 요약")
        logger.info("="*60)
        logger.info(f"업로드 대상: {today_log_file}")
        logger.info(f"성공: {success_count}개")
        logger.info(f"실패: {fail_count}개")
        if total_files > 0:
            success_rate = (success_count / total_files) * 100
            logger.info(f"성공률: {success_rate:.1f}%")
        logger.info("="*60)
        
        return {
            'success': success_count > 0,
            'total_files': total_files,
            'uploaded_files': uploaded_files,
            'failed_files': failed_files,
            'success_count': success_count,
            'fail_count': fail_count
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

def cleanup_old_errorlogs(days_to_keep=30, logger=None):
    """30일 기준으로 오래된 에러로그 정리"""
    if logger is None:
        logger = logging.getLogger(__name__)
    
    logger.info("=== 오래된 에러로그 정리 시작 ===")
    
    try:
        # 기준 날짜 계산 (30일 전)
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
        logger.info(f"🗓️ {days_to_keep}일 이전 데이터 정리 기준: {cutoff_date.strftime('%Y-%m-%d')}")
        
        # 에러로그 폴더들 가져오기
        errorlog_folders = get_errorlog_folders()
        if not errorlog_folders:
            logger.info("📁 정리할 에러로그 폴더가 없습니다.")
            return {
                'success': True,
                'deleted_folders': [],
                'total_size_freed': 0
            }
        
        deleted_folders = []
        total_size_freed = 0
        
        for folder_name in errorlog_folders:
            try:
                # 폴더명을 날짜로 파싱
                folder_date = datetime.datetime.strptime(folder_name, '%Y-%m-%d')
                
                # 기준 날짜보다 오래된 폴더인지 확인
                if folder_date < cutoff_date:
                    folder_path = os.path.join(ERRORLOG_BASE_DIR, folder_name)
                    
                    # 폴더 내 파일들의 총 크기 계산
                    folder_size = 0
                    if os.path.exists(folder_path):
                        for root, dirs, files in os.walk(folder_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                folder_size += os.path.getsize(file_path)
                    
                    # 폴더 삭제
                    shutil.rmtree(folder_path)
                    deleted_folders.append({
                        'name': folder_name,
                        'date': folder_date.strftime('%Y-%m-%d'),
                        'size': folder_size
                    })
                    total_size_freed += folder_size
                    
                    logger.info(f"🗑️ {folder_name} 폴더 삭제 완료 (크기: {folder_size:,} bytes)")
                else:
                    logger.info(f"📁 {folder_name} 폴더는 {days_to_keep}일 이내로 유지")
                    
            except ValueError as e:
                logger.warning(f"⚠️ {folder_name} 폴더명을 날짜로 파싱할 수 없습니다: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"❌ {folder_name} 폴더 정리 중 오류: {str(e)}")
                continue
        
        # 정리 결과 출력
        logger.info("="*60)
        logger.info("🗑️ 에러로그 정리 결과 요약")
        logger.info("="*60)
        logger.info(f"삭제된 폴더 수: {len(deleted_folders)}개")
        logger.info(f"정리된 총 용량: {total_size_freed:,} bytes ({total_size_freed / (1024*1024):.2f} MB)")
        
        if deleted_folders:
            logger.info("\n삭제된 폴더 목록:")
            for folder in deleted_folders:
                logger.info(f"  └─ {folder['name']} ({folder['date']}) - {folder['size']:,} bytes")
        
        logger.info("="*60)
        
        return {
            'success': True,
            'deleted_folders': deleted_folders,
            'total_size_freed': total_size_freed
        }
        
    except Exception as e:
        error_msg = f"에러로그 정리 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        logger.error(f"상세 에러: {traceback.format_exc()}")
        return {
            'success': False,
            'message': error_msg,
            'deleted_folders': [],
            'total_size_freed': 0
        }

def main():
    """메인 실행 함수"""
    print("🚀 에러로그 자동 업로드 및 정리 테스트 시작")
    print("="*80)
    
    # 로깅 설정
    logger = setup_logging()
    
    try:
        # 1단계: 오래된 에러로그 정리 (30일 기준)
        print("\n📋 1단계: 오래된 에러로그 정리")
        cleanup_result = cleanup_old_errorlogs(days_to_keep=30, logger=logger)
        
        if cleanup_result['success']:
            print(f"✅ 에러로그 정리 완료: {len(cleanup_result['deleted_folders'])}개 폴더 삭제")
        else:
            print(f"❌ 에러로그 정리 실패: {cleanup_result['message']}")
        
        # 2단계: 에러로그 구글드라이브 업로드 (오늘 날짜 로그만)
        print("\n📋 2단계: 에러로그 구글드라이브 업로드 (오늘 날짜 로그만)")
        upload_result = upload_errorlog_to_drive(logger)
        
        if upload_result['success']:
            print(f"✅ 오늘 날짜 에러로그 업로드 완료")
        else:
            print(f"❌ 에러로그 업로드 실패: {upload_result['message']}")
        
        # 3단계: 최종 결과 요약
        print("\n" + "="*80)
        print("📊 최종 실행 결과 요약")
        print("="*80)
        
        # 정리 결과
        if cleanup_result['success']:
            print(f"🗑️ 에러로그 정리: {len(cleanup_result['deleted_folders'])}개 폴더 삭제")
            if cleanup_result['total_size_freed'] > 0:
                print(f"   └─ 정리된 용량: {cleanup_result['total_size_freed'] / (1024*1024):.2f} MB")
        else:
            print(f"🗑️ 에러로그 정리: 실패 - {cleanup_result['message']}")
        
        # 업로드 결과
        if upload_result['success']:
            print(f"☁️ 구글드라이브 업로드: 오늘 날짜 에러로그 업로드 성공")
        else:
            print(f"☁️ 구글드라이브 업로드: 실패 - {upload_result['message']}")
        
        print("="*80)
        print("🎉 에러로그 자동 업로드 및 정리 테스트 완료!")
        
    except Exception as e:
        error_msg = f"메인 실행 중 오류 발생: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(f"상세 에러: {traceback.format_exc()}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 모든 작업이 성공적으로 완료되었습니다.")
        sys.exit(0)
    else:
        print("\n❌ 작업 실행 중 오류가 발생했습니다.")
        sys.exit(1)
