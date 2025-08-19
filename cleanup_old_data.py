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
    
    # 모든 대상 폴더를 한 번에 스캔하여 정리
    cleanup_all_folders_batch(logger, cutoff_date)
    
    logger.info(f"=== 오래된 데이터 정리 완료 ===")



def cleanup_all_folders_batch(logger, cutoff_date):
    """모든 대상 폴더를 한 번에 스캔하여 배치로 정리"""
    logger.info(f"\n📁 전체 폴더 정리 시작 (배치 처리)")
    
    # 정리 대상 폴더들 정의
    target_folders = [
        ('scheduleData', 'YYMMDD'),
        ('ErrorLog', 'YYYY-MM-DD')
    ]
    
    all_folders_to_delete = []
    all_folders_to_keep = []
    
    # 모든 대상 폴더를 한 번에 스캔
    for base_folder, date_pattern in target_folders:
        base_path = os.path.join(os.getcwd(), base_folder)
        
        if not os.path.exists(base_path):
            logger.warning(f"{base_folder} 폴더가 존재하지 않습니다: {base_path}")
            continue
        
        logger.info(f"📂 {base_folder} 폴더 스캔 중...")
        
        # 폴더 스캔 및 분류
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            
            if os.path.isdir(item_path):
                folder_date = parse_date_folder(item)
                
                if folder_date:
                    if folder_date < cutoff_date:
                        all_folders_to_delete.append((base_folder, item, folder_date))
                    else:
                        all_folders_to_keep.append((base_folder, item, folder_date))
                else:
                    # 날짜 형식이 아닌 폴더는 유지
                    all_folders_to_keep.append((base_folder, item, None))
    
    # 삭제할 폴더들 출력
    if all_folders_to_delete:
        logger.info(f"🗑️ 삭제할 폴더들 ({len(all_folders_to_delete)}개):")
        for base_folder, folder_name, folder_date in all_folders_to_delete:
            date_str = folder_date.strftime('%Y-%m-%d') if folder_date else 'N/A'
            logger.info(f"  - {base_folder}/{folder_name} ({date_str})")
        
        # 배치 삭제 실행
        deleted_count = 0
        for base_folder, folder_name, folder_date in all_folders_to_delete:
            folder_path = os.path.join(os.getcwd(), base_folder, folder_name)
            try:
                shutil.rmtree(folder_path)
                date_str = folder_date.strftime('%Y-%m-%d') if folder_date else 'N/A'
                logger.info(f"✅ 삭제 완료: {base_folder}/{folder_name} ({date_str})")
                deleted_count += 1
            except Exception as e:
                logger.error(f"❌ 삭제 실패: {base_folder}/{folder_name} - {str(e)}")
        
        logger.info(f"📊 삭제 결과: {deleted_count}/{len(all_folders_to_delete)}개 폴더 삭제 완료")
    else:
        logger.info("🗑️ 삭제할 폴더가 없습니다.")
    
    # 유지할 폴더들 출력
    if all_folders_to_keep:
        logger.info(f"📁 유지할 폴더들 ({len(all_folders_to_keep)}개):")
        for base_folder, folder_name, folder_date in all_folders_to_keep:
            if folder_date:
                date_str = folder_date.strftime('%Y-%m-%d')
                logger.info(f"  - {base_folder}/{folder_name} ({date_str})")
            else:
                logger.info(f"  - {base_folder}/{folder_name} (특수 폴더)")

def main():
    """메인 실행 함수"""
    print("🧹 오래된 데이터 정리 시작...")
    cleanup_old_folders(days_to_keep=30)
    print("✅ 정리 완료!")

if __name__ == "__main__":
    main() 