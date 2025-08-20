### 해당 코드 역할 요약 ###
# 실제 역할:
# - 설정 파일에서 선사 목록 로드
# - 크롤러 팩토리 호출하여 크롤러 생성
# - 개별 크롤러 실행 및 에러 처리
# - 결과 집계 및 로깅
# - Excel 로그 생성
# - 구글 드라이브 업로드 호출
# - 데이터 정리 스크립트 호출
# - 에러로그 자동 업로드 및 정리

# 하지 않는 것:
# - 직접 크롤러 인스턴스 생성하지 않음
# - 데이터 파이프라인 직접 관리하지 않음


# 여기서부터 시작함.
from crawler import base
from crawler import sitc
from crawler import evergreen
from crawler import cosco
from crawler import wanhai
from crawler import one
from crawler import ckline
from crawler import panocean
from crawler import snl
from crawler import smline
from crawler import hmm
from crawler import fdt
from crawler import ial # 완료
from crawler import dyline
from crawler import yml  # 완료
from crawler import nss

import traceback
import logging
from datetime import datetime
import os
import sys
import pandas as pd
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# ErrorLog 폴더 구조 생성
def setup_errorlog_folder():
    """ErrorLog 폴더 구조 생성"""
    log_base_dir = os.path.join(os.getcwd(), "ErrorLog")
    if not os.path.exists(log_base_dir):
        os.makedirs(log_base_dir)
    
    # 날짜별 폴더 생성 (YYYY-MM-DD 형식)
    today_log_folder = datetime.now().strftime("%Y-%m-%d")
    today_log_dir = os.path.join(log_base_dir, today_log_folder)
    if not os.path.exists(today_log_dir):
        os.makedirs(today_log_dir)
    
    return today_log_dir

# ErrorLog 폴더 설정
today_log_dir = setup_errorlog_folder()

# 에러로그 구글드라이브 폴더 ID
ERRORLOG_DRIVE_FOLDER_ID = '1t3P2oofZKnSrVMmDS6-YQcwuZC6PdCz5'

# 메인 로깅 설정 (콘솔만)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# 크롤러 팩토리 import
from crawler_factory import CrawlerFactory

# Google Drive 관련 함수들 import
import sys
sys.path.append(os.path.join(os.getcwd(), 'Google'))
from Google.upload_to_drive_oauth import get_drive_service, upload_file_to_drive

# 빌더 패턴을 위한 크롤링 프로세스 클래스
class CrawlingProcess:
    """크롤링 프로세스의 최종 결과를 담는 클래스"""
    def __init__(self):
        self.crawling_results = []
        self.total_duration = 0
        self.success_count = 0
        self.fail_count = 0
        self.total_vessels_success = 0
        self.total_vessels_fail = 0
        self.excel_log_path = None
        self.upload_result = None
        self.cleanup_result = None

class CrawlingProcessBuilder:
    """크롤링 프로세스를 단계별로 구성하는 빌더 클래스"""
    
    def __init__(self):
        self.process = CrawlingProcess()
        self.carriers_config = None
        self.max_workers = 2
        self.logger = None
        self.total_start_time = None
        self.total_end_time = None
    
    def setup_environment(self):
        """환경 설정 단계: 폴더 생성, 설정 로드, 로깅 설정"""
        print("환경 설정 단계 시작")
        
        # ErrorLog 폴더 설정
        self.process.today_log_dir = setup_errorlog_folder()
        
        # 로거 설정
        self.logger = logging.getLogger(__name__)
        
        # 설정 파일 로드
        self.carriers_config = load_carriers_config()
        
        print("환경 설정 단계 완료")
        return self
    
    def configure_threading(self, max_workers=2):
        """스레드 설정 단계: 병렬 처리 설정"""
        self.max_workers = max_workers
        print(f"스레드 설정: {max_workers}개 워커")
        return self
    
    def add_carriers(self, carriers_config=None):
        """선사 설정 단계: 크롤링할 선사 목록 설정"""
        if carriers_config:
            self.carriers_config = carriers_config
        
        if not self.carriers_config:
            raise ValueError("선사 설정이 로드되지 않았습니다.")
        
        carriers_to_run = []
        for carrier_info in self.carriers_config['carriers']:
            carrier_name = carrier_info['name']
            carriers_to_run.append(carrier_name)
        
        self.process.carriers_to_run = carriers_to_run
        print(f"선사 설정 완료: {len(carriers_to_run)}개 선사")
        return self
    
    def execute_crawling(self):
        """크롤링 실행 단계: 실제 크롤링 수행"""
        if not hasattr(self.process, 'carriers_to_run'):
            raise ValueError("선사 목록이 설정되지 않았습니다.")
        
        print("크롤링 실행 단계 시작")
        print(f"총 {len(self.process.carriers_to_run)}개 선사 크롤링 시작")
        print(f"스레드 수: {self.max_workers}개 (선사 {self.max_workers}개씩 병렬 처리)")
        print("="*80)
        
        # 전체 크롤링 시작 시간
        self.total_start_time = datetime.now()
        self.logger.info(f"=== 전체 크롤링 시작: {self.total_start_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        
        # 스레드 기반 병렬 실행
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 모든 선사를 스레드 풀에 제출
            future_to_carrier = {executor.submit(run_carrier_parallel, carrier_name): carrier_name 
                               for carrier_name in self.process.carriers_to_run}
            
            # 완료된 작업들을 순서대로 처리
            for future in as_completed(future_to_carrier):
                carrier_name = future_to_carrier[future]
                try:
                    result = future.result()
                    self.process.crawling_results.append(result)
                    print(f" {carrier_name} 완료 - 스레드에서 반환됨")
                except Exception as e:
                    print(f" {carrier_name} 스레드 실행 중 오류: {str(e)}")
                    self.process.crawling_results.append((carrier_name, {
                        'success': False,
                        'duration': 0,
                        'start_time': None,
                        'end_time': datetime.now(),
                        'error': f'스레드 실행 중 오류: {str(e)}',
                        'traceback': traceback.format_exc()
                    }))
        
        # 전체 크롤링 종료 시간
        self.total_end_time = datetime.now()
        self.process.total_duration = (self.total_end_time - self.total_start_time).total_seconds()
        
        print("크롤링 실행 단계 완료")
        return self
    
    def generate_reports(self):
        """보고서 생성 단계: 결과 요약 및 Excel 로그 생성"""
        print("보고서 생성 단계 시작")
        
        # 크롤링 결과 요약 출력
        print("\n" + "="*80)
        print("크롤링 결과 요약")
        print("="*80)
        
        success_count = 0
        fail_count = 0
        total_vessels_success = 0
        total_vessels_fail = 0
        
        for carrier_name, result in self.process.crawling_results:
            status = "성공" if result['success'] else "실패"
            duration_str = f"({result['duration']:.2f}초)" if 'duration' in result else ""
            print(f"{carrier_name}: {status} {duration_str}")
            
            if result['success']:
                success_count += 1
                if 'success_count' in result:
                    total_vessels_success += result['success_count']
                    total_vessels_fail += result['fail_count']
                    print(f"  └─ 선박: 성공 {result['success_count']}개, 실패 {result['fail_count']}개")
            else:
                fail_count += 1
                if 'total_vessels' in result and 'fail_count' in result:
                    total_vessels_success += result.get('success_count', 0)
                    total_vessels_fail += result['fail_count']
                    print(f"  └─ 선박: 성공 {result.get('success_count', 0)}개, 실패 {result['fail_count']}개")
                    if result.get('failed_vessels'):
                        print(f"  └─ 실패한 선박: {', '.join(result['failed_vessels'])}")
                elif 'error' in result:
                    print(f"  └─ 에러: {result['error']}")
        
        print(f"\n병렬 처리 결과:")
        print(f"총 {len(self.process.crawling_results)}개 선사 중")
        print(f"성공: {success_count}개")
        print(f"실패: {fail_count}개")
        print(f"총 소요시간: {self.process.total_duration:.2f}초")
        
        # 기존 순차 처리와 비교 (이론적)
        estimated_sequential_time = self.process.total_duration * self.max_workers
        time_saved = estimated_sequential_time - self.process.total_duration
        print(f"예상 순차 처리 시간: {estimated_sequential_time:.2f}초")
        print(f"절약된 시간: {time_saved:.2f}초 ({time_saved/estimated_sequential_time*100:.1f}%)")
        
        if total_vessels_success > 0 or total_vessels_fail > 0:
            print(f"\n선박별 상세 결과:")
            print(f"총 선박: {total_vessels_success + total_vessels_fail}개")
            print(f"성공: {total_vessels_success}개")
            print(f"실패: {total_vessels_fail}개")
        
        print("="*80)
        
        # 결과 저장
        self.process.success_count = success_count
        self.process.fail_count = fail_count
        self.process.total_vessels_success = total_vessels_success
        self.process.total_vessels_fail = total_vessels_fail
        
        # 로그 파일에도 요약 기록
        self.logger.info(f"=== 전체 크롤링 완료: {self.total_end_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        self.logger.info(f"총 소요시간: {self.process.total_duration:.2f}초")
        self.logger.info(f"성공: {success_count}개 선사, 실패: {fail_count}개 선사")
        if total_vessels_success > 0 or total_vessels_fail > 0:
            self.logger.info(f"선박별 - 성공: {total_vessels_success}개, 실패: {total_vessels_fail}개")
        
        # 엑셀 로그 저장
        save_excel_log(self.process.crawling_results, self.process.total_duration)
        
        print("보고서 생성 단계 완료")
        return self
    
    def upload_to_drive(self):
        """드라이브 업로드 단계: 구글 드라이브 업로드"""
        print("드라이브 업로드 단계 시작")
        
        print("\n" + "="*80)
        print("구글 드라이브 업로드 시작")
        print("="*80)
        
        # 구글 업로드 로그를 위한 리스트
        google_upload_logs = []
        
        try:
            # Google 폴더의 업로드 스크립트 import
            sys.path.append(os.path.join(os.getcwd(), 'Google'))
            from Google.upload_to_drive_oauth import main as upload_to_drive_main, get_drive_service, upload_file_to_drive
        
            # 업로드 실행
            upload_result = upload_to_drive_main()
            
            # 업로드 결과를 로그에 기록
            if upload_result and isinstance(upload_result, dict):
                for file_info in upload_result.get('uploaded_files', []):
                    google_upload_logs.append({
                        '날짜': datetime.now().strftime('%Y/%m/%d/%H/%M/%S'),
                        '선사': 'Google Drive',
                        '선박': file_info.get('filename', '알 수 없음'),
                        '상태': '성공',
                        '사유/결과': f"업로드 완료 (파일 ID: {file_info.get('file_id', 'N/A')})",
                        '소요시간': 'N/A'
                    })
                
                for file_info in upload_result.get('failed_files', []):
                    google_upload_logs.append({
                        '날짜': datetime.now().strftime('%Y/%m/%d/%H/%M/%S'),
                        '선사': 'Google Drive',
                        '선박': file_info.get('filename', '알 수 없음'),
                        '상태': '실패',
                        '사유/결과': f"업로드 실패: {file_info.get('error', '알 수 없는 오류')}",
                        '소요시간': 'N/A'
                    })
            
            print("="*80)
            print("구글 드라이브 업로드 완료")
            print("="*80)
            
            # 구글 업로드 로그를 엑셀에 추가
            excel_log_data.extend(google_upload_logs)
            
            self.process.upload_result = upload_result
            
        except Exception as e:
            error_msg = f"구글 드라이브 업로드 실패: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            
            # 업로드 실패 로그를 엑셀에 추가
            google_upload_logs.append({
                '날짜': datetime.now().strftime('%Y/%m/%d/%H/%M/%S'),
                '선사': 'Google Drive',
                '선박': '전체 업로드',
                '상태': '실패',
                '사유/결과': error_msg,
                '소요시간': 'N/A'
            })
            excel_log_data.extend(google_upload_logs)
        
        print("드라이브 업로드 단계 완료")
        return self
    
    def cleanup_resources(self):
        """리소스 정리 단계: 오래된 데이터 및 에러로그 정리"""
        print("리소스 정리 단계 시작")
        
        # 오래된 데이터 정리
        print("\n" + "="*80)
        print("오래된 데이터 정리 시작")
        print("="*80)
        
        try:
            from cleanup_old_data import cleanup_old_folders
            
            # 1달(30일) 이전 폴더들 정리
            cleanup_old_folders(days_to_keep=30)
            
            print("="*80)
            print("오래된 데이터 정리 완료")
            print("="*80)
            
        except Exception as e:
            print(f"오래된 데이터 정리 실패: {str(e)}")
            self.logger.error(f"오래된 데이터 정리 실패: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
        
        # 에러로그 자동 업로드 및 정리
        print("\n" + "="*80)
        print("에러로그 자동 업로드 및 정리 시작")
        print("="*80)
        
        try:
            # 1단계: 오래된 에러로그 정리 (30일 기준)
            print("\n1단계: 오래된 에러로그 정리")
            errorlog_cleanup_result = cleanup_old_errorlogs(days_to_keep=30, logger=self.logger)
            
            if errorlog_cleanup_result['success']:
                print(f"에러로그 정리 완료: {len(errorlog_cleanup_result['deleted_folders'])}개 폴더 삭제")
                if errorlog_cleanup_result['total_size_freed'] > 0:
                    print(f"   └─ 정리된 용량: {errorlog_cleanup_result['total_size_freed'] / (1024*1024):.2f} MB")
            else:
                print(f"에러로그 정리 실패: {errorlog_cleanup_result['message']}")
            
            # 2단계: 에러로그 구글드라이브 업로드 (오늘 날짜 로그만)
            print("\n2단계: 에러로그 구글드라이브 업로드 (오늘 날짜 로그만)")
            errorlog_upload_result = upload_errorlog_to_drive(self.logger)
            
            if errorlog_upload_result['success']:
                print(f"오늘 날짜 에러로그 업로드 완료")
            else:
                print(f"에러로그 업로드 실패: {errorlog_upload_result['message']}")
            
            print("="*80)
            print("에러로그 자동 업로드 및 정리 완료")
            print("="*80)
            
            self.process.cleanup_result = {
                'errorlog_cleanup': errorlog_cleanup_result,
                'errorlog_upload': errorlog_upload_result
            }
            
        except Exception as e:
            error_msg = f"에러로그 자동 업로드 및 정리 실패: {str(e)}"
            print(f"{error_msg}")
            self.logger.error(error_msg)
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
        
        print("리소스 정리 단계 완료")
        return self
    
    def build(self):
        """최종 프로세스 반환"""
        return self.process

# 설정 파일에서 선사 정보 로드
def load_carriers_config():
    """선사 설정 파일을 로드합니다."""
    try:
        import json
        config_path = os.path.join(os.getcwd(), 'config', 'carriers.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"설정 파일 로드 실패: {str(e)}")
        # 기본값 반환
        return {"carriers": []}

# 엑셀 로그 데이터를 저장할 리스트 (스레드 안전을 위해 Lock 사용)
excel_log_data = []
excel_log_lock = threading.Lock()

def add_to_excel_log(carrier_name, vessel_name, status, reason, duration):
    """엑셀 로그에 기록 추가 (성공/실패 모두) - 스레드 안전"""
    global excel_log_data
    with excel_log_lock:
        now = datetime.now()
        excel_log_data.append({
            '날짜': now.strftime('%Y/%m/%d/%H/%M/%S'),
            '선사': carrier_name,
            '선박': vessel_name,
            '상태': status,
            '사유/결과': reason,
            '소요시간': f"{duration:.2f}초"
        })

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

def upload_errorlog_to_drive(logger):
    """에러로그를 구글드라이브에 업로드 (오늘 날짜의 _log.xlsx 파일만)"""
    logger.info("=== 에러로그 구글드라이브 업로드 시작 ===")
    
    try:
        # 드라이브 서비스 생성
        service = get_drive_service()
        logger.info("✅ 구글 드라이브 서비스 연결 성공")
        
        # 오늘 날짜의 에러로그 파일 찾기
        today = datetime.now()
        today_folder = today.strftime('%Y-%m-%d')
        today_log_file = f"{today.strftime('%Y%m%d')}_log.xlsx"
        
        # 오늘 날짜 폴더 경로
        today_folder_path = os.path.join(os.getcwd(), "ErrorLog", today_folder)
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
            file_modified = datetime.fromtimestamp(os.path.getmtime(today_log_path))
            
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
        cutoff_date = datetime.now() - datetime.timedelta(days=days_to_keep)
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

def save_excel_log(crawling_results, total_duration):
    """엑셀 로그 파일 저장 (요약 정보 포함)"""
    if not excel_log_data:
        return
    
    try:
        # 기본 로그 데이터
        df = pd.DataFrame(excel_log_data)
        
        # 요약 정보 계산
        success_count = 0
        fail_count = 0
        total_vessels_success = 0
        total_vessels_fail = 0
        
        for carrier_name, result in crawling_results:
            if result['success']:
                success_count += 1
                if 'success_count' in result:
                    total_vessels_success += result['success_count']
                    total_vessels_fail += result.get('fail_count', 0)
            else:
                fail_count += 1
                if 'total_vessels' in result and 'fail_count' in result:
                    total_vessels_success += result.get('success_count', 0)
                    total_vessels_fail += result['fail_count']
        
        # 요약 행 추가
        summary_rows = [
            {'날짜': '', '선사': '', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': '=== 크롤링 결과 요약 ===', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'총 {len(crawling_results)}개 선사 중', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'성공: {success_count}개', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'실패: {fail_count}개', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'총 소요시간: {total_duration:.2f}초', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': '', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': '=== 선박별 상세 결과 ===', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'총 선박: {total_vessels_success + total_vessels_fail}개', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'성공: {total_vessels_success}개', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''},
            {'날짜': '', '선사': f'실패: {total_vessels_fail}개', '선박': '', '상태': '', '사유/결과': '', '소요시간': ''}
        ]
        
        # 요약 행을 DataFrame에 추가
        summary_df = pd.DataFrame(summary_rows)
        final_df = pd.concat([df, summary_df], ignore_index=True)
        
        today_str = datetime.now().strftime('%Y%m%d')
        excel_filename = f"{today_str}_log.xlsx"
        excel_path = os.path.join(today_log_dir, excel_filename)
        
        final_df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"✅ 엑셀 로그 저장 완료: {excel_path}")
        
    except Exception as e:
        print(f"❌ 엑셀 로그 저장 실패: {str(e)}")
        logging.error(f"엑셀 로그 저장 실패: {str(e)}")

def run_crawler_with_error_handling(crawler_name, crawler_instance):
    """크롤러를 실행하고 에러를 처리하는 함수"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"=== {crawler_name} 크롤링 시작 ===")
        start_time = datetime.now()
        
        # 첫 번째 시도
        result = crawler_instance.run()
        
        # 실패한 선박이 있는지 확인하고 재시도
        retry_result = None
        if hasattr(crawler_instance, 'failed_vessels') and crawler_instance.failed_vessels:
                failed_vessels = crawler_instance.failed_vessels.copy()
                failed_reasons = getattr(crawler_instance, 'failed_reasons', {}).copy()
                
                logger.info(f"=== {crawler_name} 실패한 선박 재시도 시작 ===")
                logger.info(f"재시도 대상 선박: {', '.join(failed_vessels)}")
                logger.info(f"재시도 대상 개수: {len(failed_vessels)}개")
                
                # 실패한 선박들만 재시도
                retry_result = crawler_instance.retry_failed_vessels(failed_vessels)
                
                if retry_result:
                    logger.info(f"=== {crawler_name} 재시도 완료 ===")
                    logger.info(f"재시도 성공: {retry_result.get('retry_success', 0)}개")
                    logger.info(f"재시도 실패: {retry_result.get('retry_fail', 0)}개")
                    logger.info(f"재시도 후 최종 성공: {retry_result.get('final_success', 0)}개")
                    logger.info(f"재시도 후 최종 실패: {retry_result.get('final_fail', 0)}개")
                    
                    if 'note' in retry_result:
                        logger.info(f"재시도 참고사항: {retry_result['note']}")
                else:
                    logger.warning(f"=== {crawler_name} 재시도 실패 ===")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 크롤러에 성공/실패 카운트가 있는 경우 선박별 결과 확인
        if hasattr(crawler_instance, 'success_count') and hasattr(crawler_instance, 'fail_count'):
            # 실제 선박 대수는 vessel_name_list의 길이로 계산
            total_vessels = len(getattr(crawler_instance, 'vessel_name_list', []))
            success_count = getattr(crawler_instance, 'success_count', 0)
            fail_count = getattr(crawler_instance, 'fail_count', 0)
            failed_vessels = getattr(crawler_instance, 'failed_vessels', [])
            failed_reasons = getattr(crawler_instance, 'failed_reasons', {})
            
            # 성공한 선박들을 엑셀 로그에 기록
            if hasattr(crawler_instance, 'vessel_name_list'):
                for vessel_name in crawler_instance.vessel_name_list:
                    if vessel_name not in failed_vessels:
                        vessel_duration = getattr(crawler_instance, 'get_vessel_duration', lambda x: duration)(vessel_name)
                        add_to_excel_log(crawler_name, vessel_name, "성공", "크롤링 완료", vessel_duration)
            
            # 실패한 선박들을 엑셀 로그에 기록
            for vessel_name in failed_vessels:
                reason = failed_reasons.get(vessel_name, "알 수 없는 오류")
                vessel_duration = getattr(crawler_instance, 'get_vessel_duration', lambda x: duration)(vessel_name)
                add_to_excel_log(crawler_name, vessel_name, "실패", reason, vessel_duration)
            
            # 재시도 결과가 있는 경우 최종 결과 반영
            final_success_count = success_count
            final_fail_count = fail_count
            final_failed_vessels = failed_vessels.copy()
            
            if retry_result:
                final_success_count = retry_result.get('final_success', success_count)
                final_fail_count = retry_result.get('final_fail', fail_count)
                # 재시도 후 최종 실패한 선박들 업데이트
                if 'final_failed_vessels' in retry_result:
                    final_failed_vessels = retry_result['final_failed_vessels']
            
            # 선박 중 하나라도 실패하면 선사도 실패로 분류
            if final_fail_count > 0:
                logger.error(f"=== {crawler_name} 크롤링 실패 (소요시간: {duration:.2f}초) ===")
                logger.error(f"선박 실패로 인한 선사 실패: 총 {total_vessels}개 선박 중 성공 {final_success_count}개, 실패 {final_fail_count}개")
                if final_failed_vessels:
                    logger.error(f"실패한 선박: {', '.join(final_failed_vessels)}")
                
                return {
                    'success': False,
                    'duration': duration,
                    'start_time': start_time,
                    'end_time': end_time,
                    'total_vessels': total_vessels,
                    'success_count': final_success_count,
                    'fail_count': final_fail_count,
                    'failed_vessels': final_failed_vessels,
                    'error': f'선박 실패로 인한 선사 실패 (실패한 선박: {", ".join(final_failed_vessels)})'
                }
            else:
                logger.info(f"=== {crawler_name} 크롤링 완료 (소요시간: {duration:.2f}초) ===")
                logger.info(f"{crawler_name} 상세 결과: 총 {total_vessels}개 선박 중 성공 {final_success_count}개, 실패 {final_fail_count}개")
                
                return {
                    'success': True,
                    'duration': duration,
                    'start_time': start_time,
                    'end_time': end_time,
                    'total_vessels': total_vessels,
                    'success_count': final_success_count,
                    'fail_count': final_fail_count,
                    'failed_vessels': final_failed_vessels
                }
        else:
            # 성공/실패 카운트가 없는 경우 기존 로직 사용
            if result:
                logger.info(f"=== {crawler_name} 크롤링 완료 (소요시간: {duration:.2f}초) ===")
                return {
                    'success': True,
                    'duration': duration,
                    'start_time': start_time,
                    'end_time': end_time
                }
            else:
                logger.error(f"=== {crawler_name} 크롤링 실패 (소요시간: {duration:.2f}초) ===")
                return {
                    'success': False,
                    'duration': duration,
                    'start_time': start_time,
                    'end_time': end_time,
                    'error': '크롤러 실행 중 오류 발생'
                }
            
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time) if 'start_time' in locals() else 0
        
        logger.error(f"=== {crawler_name} 크롤링 실패 ===")
        logger.error(f"에러 메시지: {str(e)}")
        logger.error(f"상세 에러: {traceback.format_exc()}")
        
        return {
            'success': False,
            'duration': duration.total_seconds() if hasattr(duration, 'total_seconds') else 0,
            'start_time': start_time if 'start_time' in locals() else None,
            'end_time': end_time,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def try_run_carrier(crawler_name, constructor, results_list):
    """크롤러 인스턴스화 단계에서의 예외도 잡아서 다음 선사로 넘어가도록 처리"""
    logger = logging.getLogger(__name__)
    try:
        # 크롤러 팩토리를 사용하여 인스턴스 생성
        instance = CrawlerFactory.create_crawler(crawler_name)
    except Exception as e:
        end_time = datetime.now()
        logger.error(f"=== {crawler_name} 크롤러 인스턴스 생성 실패 ===")
        logger.error(f"에러 메시지: {str(e)}")
        logger.error(f"상세 에러: {traceback.format_exc()}")
        results_list.append((crawler_name, {
            'success': False,
            'duration': 0,
            'start_time': None,
            'end_time': end_time,
            'error': str(e),
            'traceback': traceback.format_exc()
        }))
        return
    # 인스턴스 생성에 성공하면 실행
    result = run_crawler_with_error_handling(crawler_name, instance)
    results_list.append((crawler_name, result))

def run_carrier_parallel(crawler_name):
    """스레드에서 실행할 크롤러 함수"""
    logger = logging.getLogger(__name__)
    try:
        # 크롤러 인스턴스 생성
        instance = CrawlerFactory.create_crawler(crawler_name)
        # 크롤러 실행
        result = run_crawler_with_error_handling(crawler_name, instance)
        return crawler_name, result
    except Exception as e:
        end_time = datetime.now()
        logger.error(f"=== {crawler_name} 크롤러 실행 실패 ===")
        logger.error(f"에러 메시지: {str(e)}")
        logger.error(f"상세 에러: {traceback.format_exc()}")
        return crawler_name, {
            'success': False,
            'duration': 0,
            'start_time': None,
            'end_time': end_time,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

if __name__ == "__main__":
    print("빌더 패턴을 사용한 스레드 기반 병렬 크롤링 시작!")
    print("="*80)
    
    try:
        # 빌더 패턴을 사용하여 크롤링 프로세스 구성 및 실행
        crawling_process = (CrawlingProcessBuilder()
            .setup_environment()           # 1단계: 환경 설정
            .configure_threading(2)       # 2단계: 스레드 설정 (2개)
            .add_carriers()               # 3단계: 선사 설정
            .execute_crawling()           # 4단계: 크롤링 실행
            .generate_reports()           # 5단계: 보고서 생성
            .upload_to_drive()            # 6단계: 드라이브 업로드
            .cleanup_resources()          # 7단계: 리소스 정리
            .build())                     # 최종 프로세스 반환
        
        print("\n" + "="*80)
        print("빌더 패턴을 사용한 크롤링 프로세스 완료!")
        print("="*80)
        
        # 최종 결과 요약
        print(f"총 소요시간: {crawling_process.total_duration:.2f}초")
        print(f"성공: {crawling_process.success_count}개 선사")
        print(f"실패: {crawling_process.fail_count}개 선사")
        
        if crawling_process.total_vessels_success > 0 or crawling_process.total_vessels_fail > 0:
            print(f"선박별 - 성공: {crawling_process.total_vessels_success}개, 실패: {crawling_process.total_vessels_fail}개")
        
        print("="*80)
        
    except Exception as e:
        print(f"크롤링 프로세스 실행 중 오류 발생: {str(e)}")
        print(f"상세 에러: {traceback.format_exc()}")
        sys.exit(1)

    

    