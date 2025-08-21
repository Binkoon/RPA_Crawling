# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : 데이터 정리 공통 모듈

import os
import shutil
import traceback
from datetime import datetime, timedelta

def get_errorlog_folders():
    """ErrorLog 폴더 내의 모든 날짜별 폴더 목록 반환"""
    errorlog_base_dir = os.path.join(os.getcwd(), "ErrorLog")
    if not os.path.exists(errorlog_base_dir):
        return []
    
    folders = []
    for item in os.listdir(errorlog_base_dir):
        item_path = os.path.join(errorlog_base_dir, item)
        if os.path.isdir(item_path):
            # YYYY-MM-DD 형식인지 확인
            try:
                datetime.strptime(item, '%Y-%m-%d')
                folders.append(item)
            except ValueError:
                continue
    
    return sorted(folders)

def cleanup_old_errorlogs(days_to_keep=30, logger=None):
    """30일 기준으로 오래된 에러로그 정리"""
    if logger is None:
        import logging
        logger = logging.getLogger(__name__)
    
    logger.info("=== 오래된 에러로그 정리 시작 ===")
    
    try:
        # 기준 날짜 계산 (30일 전)
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        logger.info(f"🗑️ {days_to_keep}일 이전 데이터 정리 기준: {cutoff_date.strftime('%Y-%m-%d')}")
        
        # 에러로그 폴더들 가져오기
        errorlog_folders = get_errorlog_folders()
        if not errorlog_folders:
            logger.info(" 정리할 에러로그 폴더가 없습니다.")
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
                folder_date = datetime.strptime(folder_name, '%Y-%m-%d')
                
                # 기준 날짜보다 오래된 폴더인지 확인
                if folder_date < cutoff_date:
                    folder_path = os.path.join(os.getcwd(), "ErrorLog", folder_name)
                    
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
                    
                    logger.info(f" {folder_name} 폴더 삭제 완료 (크기: {folder_size:,} bytes)")
                else:
                    logger.info(f" {folder_name} 폴더는 {days_to_keep}일 이내로 유지")
                    
            except ValueError as e:
                logger.warning(f" {folder_name} 폴더명을 날짜로 파싱할 수 없습니다: {str(e)}")
                continue
            except Exception as e:
                logger.error(f" {folder_name} 폴더 정리 중 오류: {str(e)}")
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

def cleanup_old_data():
    """오래된 데이터 정리 (scheduleData 폴더)"""
    try:
        from cleanup_old_data import cleanup_old_folders
        # 1달(30일) 이전 폴더들 정리
        cleanup_old_folders(days_to_keep=30)
        return True
    except Exception as e:
        print(f"오래된 데이터 정리 실패: {str(e)}")
        return False
