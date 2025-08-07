# 오래된 데이터 파일 정리 스크립트
# 30일 이전의 날짜 폴더들을 삭제

import os
import shutil
from datetime import datetime, timedelta
import logging

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cleanup_log.txt', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def parse_date_folder(folder_name):
    """날짜 폴더명을 datetime 객체로 변환"""
    try:
        # YYMMDD 형식의 폴더명을 파싱 (scheduleData용)
        if len(folder_name) == 6 and folder_name.isdigit():
            year = int('20' + folder_name[:2])  # 20YY
            month = int(folder_name[2:4])
            day = int(folder_name[4:6])
            return datetime(year, month, day)
        
        # YYYY-MM-DD 형식의 폴더명을 파싱 (ErrorLog용)
        if len(folder_name) == 10 and folder_name.count('-') == 2:
            year, month, day = folder_name.split('-')
            return datetime(int(year), int(month), int(day))
            
    except ValueError:
        return None
    return None

def cleanup_old_folders(days_to_keep=30):
    """오래된 폴더들을 삭제"""
    logger = setup_logging()
    
    # 오늘 날짜
    today = datetime.now()
    cutoff_date = today - timedelta(days=days_to_keep)
    
    logger.info(f"=== 오래된 데이터 정리 시작 ===")
    logger.info(f"오늘 날짜: {today.strftime('%Y-%m-%d')}")
    logger.info(f"삭제 기준일: {cutoff_date.strftime('%Y-%m-%d')} ({days_to_keep}일 이전)")
    
    # 1. scheduleData 폴더 정리
    cleanup_schedule_data_folders(logger, cutoff_date)
    
    # 2. ErrorLog 폴더 정리
    cleanup_errorlog_folders(logger, cutoff_date)
    
    logger.info(f"=== 오래된 데이터 정리 완료 ===")

def cleanup_schedule_data_folders(logger, cutoff_date):
    """scheduleData 폴더의 오래된 폴더들을 삭제"""
    logger.info(f"\n📁 scheduleData 폴더 정리 시작")
    
    schedule_data_path = os.path.join(os.getcwd(), 'scheduleData')
    
    if not os.path.exists(schedule_data_path):
        logger.warning(f"scheduleData 폴더가 존재하지 않습니다: {schedule_data_path}")
        return
    
    # scheduleData 하위의 모든 폴더 확인
    folders_to_delete = []
    folders_to_keep = []
    
    for item in os.listdir(schedule_data_path):
        item_path = os.path.join(schedule_data_path, item)
        
        if os.path.isdir(item_path):
            # 날짜 폴더인지 확인 (YYMMDD 형식)
            folder_date = parse_date_folder(item)
            
            if folder_date:
                if folder_date < cutoff_date:
                    folders_to_delete.append((item, folder_date))
                else:
                    folders_to_keep.append((item, folder_date))
            else:
                # 날짜 형식이 아닌 폴더는 유지 (one_crawling, pil_crawling 등)
                folders_to_keep.append((item, None))
    
    # 삭제할 폴더들 출력
    if folders_to_delete:
        logger.info(f"🗑️ 삭제할 폴더들 ({len(folders_to_delete)}개):")
        for folder_name, folder_date in folders_to_delete:
            date_str = folder_date.strftime('%Y-%m-%d') if folder_date else 'N/A'
            logger.info(f"  - {folder_name} ({date_str})")
        
        # 삭제 실행
        deleted_count = 0
        for folder_name, folder_date in folders_to_delete:
            folder_path = os.path.join(schedule_data_path, folder_name)
            try:
                shutil.rmtree(folder_path)
                date_str = folder_date.strftime('%Y-%m-%d') if folder_date else 'N/A'
                logger.info(f"✅ 삭제 완료: {folder_name} ({date_str})")
                deleted_count += 1
            except Exception as e:
                logger.error(f"❌ 삭제 실패: {folder_name} - {str(e)}")
        
        logger.info(f"📊 삭제 결과: {deleted_count}/{len(folders_to_delete)}개 폴더 삭제 완료")
    else:
        logger.info("🗑️ 삭제할 폴더가 없습니다.")
    
    # 유지할 폴더들 출력
    if folders_to_keep:
        logger.info(f"📁 유지할 폴더들 ({len(folders_to_keep)}개):")
        for folder_name, folder_date in folders_to_keep:
            if folder_date:
                date_str = folder_date.strftime('%Y-%m-%d')
                logger.info(f"  - {folder_name} ({date_str})")
            else:
                logger.info(f"  - {folder_name} (특수 폴더)")

def cleanup_errorlog_folders(logger, cutoff_date):
    """ErrorLog 폴더의 오래된 폴더들을 삭제"""
    logger.info(f"\n📁 ErrorLog 폴더 정리 시작")
    
    errorlog_path = os.path.join(os.getcwd(), 'ErrorLog')
    
    if not os.path.exists(errorlog_path):
        logger.warning(f"ErrorLog 폴더가 존재하지 않습니다: {errorlog_path}")
        return
    
    # ErrorLog 하위의 모든 폴더 확인
    folders_to_delete = []
    folders_to_keep = []
    
    for item in os.listdir(errorlog_path):
        item_path = os.path.join(errorlog_path, item)
        
        if os.path.isdir(item_path):
            # 날짜 폴더인지 확인 (YYYY-MM-DD 형식)
            folder_date = parse_date_folder(item)
            
            if folder_date:
                if folder_date < cutoff_date:
                    folders_to_delete.append((item, folder_date))
                else:
                    folders_to_keep.append((item, folder_date))
            else:
                # 날짜 형식이 아닌 폴더는 유지
                folders_to_keep.append((item, None))
    
    # 삭제할 폴더들 출력
    if folders_to_delete:
        logger.info(f"🗑️ 삭제할 폴더들 ({len(folders_to_delete)}개):")
        for folder_name, folder_date in folders_to_delete:
            date_str = folder_date.strftime('%Y-%m-%d') if folder_date else 'N/A'
            logger.info(f"  - {folder_name} ({date_str})")
        
        # 삭제 실행
        deleted_count = 0
        for folder_name, folder_date in folders_to_delete:
            folder_path = os.path.join(errorlog_path, folder_name)
            try:
                shutil.rmtree(folder_path)
                date_str = folder_date.strftime('%Y-%m-%d') if folder_date else 'N/A'
                logger.info(f"✅ 삭제 완료: {folder_name} ({date_str})")
                deleted_count += 1
            except Exception as e:
                logger.error(f"❌ 삭제 실패: {folder_name} - {str(e)}")
        
        logger.info(f"📊 삭제 결과: {deleted_count}/{len(folders_to_delete)}개 폴더 삭제 완료")
    else:
        logger.info("🗑️ 삭제할 폴더가 없습니다.")
    
    # 유지할 폴더들 출력
    if folders_to_keep:
        logger.info(f"📁 유지할 폴더들 ({len(folders_to_keep)}개):")
        for folder_name, folder_date in folders_to_keep:
            if folder_date:
                date_str = folder_date.strftime('%Y-%m-%d')
                logger.info(f"  - {folder_name} ({date_str})")
            else:
                logger.info(f"  - {folder_name} (특수 폴더)")

def main():
    """메인 실행 함수"""
    print("🧹 오래된 데이터 정리 시작...")
    cleanup_old_folders(days_to_keep=30)
    print("✅ 정리 완료!")

if __name__ == "__main__":
    main() 