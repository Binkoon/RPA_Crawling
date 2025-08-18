# OAuth 인증을 사용한 구글 드라이브 업로드 스크립트

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import datetime
import pickle

# 구글 드라이브 파일 권한
SCOPES = ['https://www.googleapis.com/auth/drive']

# 공유 드라이브 ID (실제 공유 드라이브 ID로 변경 필요)
SHARED_DRIVE_ID = '1LDNUDHuVOOgsSxNLeayshu7QiBY5Qh4u'

def get_drive_service():
    """OAuth 인증을 사용한 드라이브 서비스 생성"""
    creds = None
    
    # token 폴더 경로 설정
    token_dir = os.path.join(os.getcwd(), 'token')
    token_path = os.path.join(token_dir, 'token.pickle')
    client_secret_path = os.path.join(token_dir, 'client_secret_1_738178615193-mq6bob2pgaejp6ofla52vqhssk9lk14q.apps.googleusercontent.com.json')

    # 기존 토큰이 있으면 불러오기
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # 토큰이 없거나 만료됐으면 새로 인증 수행
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # 토큰 저장
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def find_folder_in_drive(service, folder_name, parent_id=None):
    """드라이브에서 폴더 찾기"""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()

    files = results.get('files', [])
    if len(files) > 0:
        return files[0]['id']  # 첫번째 폴더 ID 반환
    else:
        return None

def create_folder_in_drive(service, folder_name, parent_id=None):
    """드라이브에 폴더 생성"""
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id] if parent_id else []
    }
    folder = service.files().create(
        body=file_metadata,
        fields='id',
        supportsAllDrives=True
    ).execute()
    return folder.get('id')

def upload_file_to_drive(service, file_path, parent_id):
    """파일을 드라이브에 업로드"""
    file_name = os.path.basename(file_path)
    file_metadata = {
        'name': file_name,
        'parents': [parent_id],
    }
    
    # 파일 확장자에 따른 MIME 타입 설정
    if file_path.endswith('.xlsx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif file_path.endswith('.pdf'):
        mimetype = 'application/pdf'
    else:
        mimetype = 'application/octet-stream'
    
    media = MediaFileUpload(file_path, mimetype=mimetype)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id',
        supportsAllDrives=True
    ).execute()
    print(f"Uploaded {file_name} to Google Drive with ID: {file.get('id')}")

def main():
    # 오늘 날짜 폴더명 (예: 250806)
    today_folder = datetime.datetime.now().strftime('%y%m%d')
    local_folder_path = os.path.join('scheduleData', today_folder)

    if not os.path.exists(local_folder_path):
        print(f"로컬 폴더 {local_folder_path}이(가) 존재하지 않습니다.")
        return

    # 파일 통계 수집
    all_files = []
    carrier_stats = {}
    
    for filename in os.listdir(local_folder_path):
        if filename.endswith(('.xlsx', '.pdf')):
            all_files.append(filename)
            # 선사명 추출 (파일명에서 첫 번째 언더스코어 이전 부분)
            carrier_name = filename.split('_')[0]
            if carrier_name not in carrier_stats:
                carrier_stats[carrier_name] = {'total': 0, 'success': 0, 'failed': []}
            carrier_stats[carrier_name]['total'] += 1

    print(f"\n 로컬 폴더: {local_folder_path}")
    print(f" 총 파일 수: {len(all_files)}개")
    print(f" 선사 수: {len(carrier_stats)}개")
    
    # 선사별 파일 수 출력
    print("\n 선사별 파일 현황:")
    for carrier, stats in carrier_stats.items():
        print(f"  {carrier}: {stats['total']}개 파일")

    service = get_drive_service()

    # 공유 드라이브 내 오늘 날짜 폴더 검색
    remote_folder_id = find_folder_in_drive(service, today_folder, parent_id=SHARED_DRIVE_ID)
    if not remote_folder_id:
        print(f"구글 드라이브에 {today_folder} 폴더가 없어서 생성합니다.")
        remote_folder_id = create_folder_in_drive(service, today_folder, parent_id=SHARED_DRIVE_ID)

    # 로컬 폴더 내 파일들 업로드
    uploaded_count = 0
    failed_count = 0
    
    print(f"\n 구글 드라이브 업로드 시작...")
    
    for filename in all_files:
        local_file_path = os.path.join(local_folder_path, filename)
        carrier_name = filename.split('_')[0]
        
        try:
            upload_file_to_drive(service, local_file_path, remote_folder_id)
            uploaded_count += 1
            carrier_stats[carrier_name]['success'] += 1
        except Exception as e:
            failed_count += 1
            carrier_stats[carrier_name]['failed'].append(filename)
            print(f"❌ 파일 업로드 실패: {filename} - {e}")
    
    # 최종 결과 출력
    print(f"\n" + "="*60)
    print(f" 업로드 결과 요약")
    print(f"="*60)
    print(f" 성공: {uploaded_count}개 파일")
    print(f" 실패: {failed_count}개 파일")
    if uploaded_count + failed_count > 0:
        print(f" 성공률: {(uploaded_count/(uploaded_count+failed_count)*100):.1f}%")
    else:
        print(f" 성공률: 0.0% (업로드할 파일이 없음)")
    
    print(f"\n 선사별 업로드 결과:")
    for carrier, stats in carrier_stats.items():
        success_rate = (stats['success']/stats['total']*100) if stats['total'] > 0 else 0
        status = "✅" if stats['success'] == stats['total'] else "⚠️" if stats['success'] > 0 else "❌"
        print(f"  {status} {carrier}: {stats['success']}/{stats['total']}개 ({success_rate:.1f}%)")
        if stats['failed']:
            print(f"    └─ 실패: {', '.join(stats['failed'])}")
    
    print(f"="*60)
    
    # 결과 반환
    return {
        'uploaded_files': [{'filename': filename, 'file_id': 'N/A'} for filename in all_files if filename in [f for f in all_files if f not in [failed for stats in carrier_stats.values() for failed in stats['failed']]]],
        'failed_files': [{'filename': filename, 'error': '업로드 실패'} for stats in carrier_stats.values() for filename in stats['failed']],
        'total_files': len(all_files),
        'success_count': uploaded_count,
        'fail_count': failed_count
    }

if __name__ == '__main__':
    main() 