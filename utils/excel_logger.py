# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : 엑셀 로그 관리 공통 모듈

import pandas as pd
from datetime import datetime
import os

# 엑셀 로그 데이터를 저장할 리스트
excel_log_data = []

def add_to_excel_log(carrier_name, vessel_name, status, reason, duration):
    """엑셀 로그에 기록 추가 (성공/실패 모두)"""
    global excel_log_data
    now = datetime.now()
    excel_log_data.append({
        '날짜': now.strftime('%Y/%m/%d/%H:%M:%S'),
        '선사': carrier_name,
        '선박': vessel_name,
        '상태': status,
        '사유/결과': reason,
        '소요시간': f"{duration:.2f}초"
    })

def save_excel_log(crawling_results, total_duration, today_log_dir):
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
        print(f" 엑셀 로그 저장 완료: {excel_path}")
        
    except Exception as e:
        print(f" 엑셀 로그 저장 실패: {str(e)}")
        import logging
        logging.error(f"엑셀 로그 저장 실패: {str(e)}")

def add_google_upload_logs(upload_result):
    """구글 업로드 로그를 엑셀에 추가"""
    global excel_log_data
    
    if not upload_result or not isinstance(upload_result, dict):
        return
    
    for file_info in upload_result.get('uploaded_files', []):
        excel_log_data.append({
            '날짜': datetime.now().strftime('%Y/%m/%d/%H:%M:%S'),
            '선사': 'Google Drive',
            '선박': file_info.get('filename', '알 수 없음'),
            '상태': '성공',
            '사유/결과': f"업로드 완료 (파일 ID: {file_info.get('file_id', 'N/A')})",
            '소요시간': 'N/A'
        })
    
    for file_info in upload_result.get('failed_files', []):
        excel_log_data.append({
            '날짜': datetime.now().strftime('%Y/%m/%d/%H:%M:%S'),
            '선사': 'Google Drive',
            '선박': file_info.get('filename', '알 수 없음'),
            '상태': '실패',
            '사유/결과': f"업로드 실패: {file_info.get('error', '알 수 없는 오류')}",
            '소요시간': 'N/A'
        })

def get_excel_log_data():
    """엑셀 로그 데이터 반환"""
    return excel_log_data
