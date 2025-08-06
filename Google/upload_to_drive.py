# 이 작업은 크롤링을 전부 다 돌린 이후에 실행할 것.

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import datetime

# 서비스 계정 JSON 경로
SERVICE_ACCOUNT_FILE = os.path.join('token', 'kmtcrpa-eece167cb0ad.json')

# 범위 (구글 드라이브 API)
SCOPES = ['https://www.googleapis.com/auth/drive']

# 공유 드라이브 ID (구글 드라이브 웹 공유 드라이브 주소에서 확인)
SHARED_DRIVE_ID = '1LDNUDHuVOOgsSxNLeayshu7QiBY5Qh4u'

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service

def find_folder_in_drive(service, folder_name, parent_id=None):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    else:
        # 루트가 공유 드라이브라면, 'root' 아님. shared drive 속성으로 따로 체크
        query += f" and '{SHARED_DRIVE_ID}' in parents"

    try:
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora='drive',
            driveId=SHARED_DRIVE_ID
        ).execute()
    except Exception as e:
        print(f"API 호출 에러: {e}")
        # 대안: 공유 드라이브에서 직접 검색
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
    
    return results

    files = results.get('files', [])
    if len(files) > 0:
        return files[0]['id']  # 첫번째 폴더 ID 반환
    else:
        return None

def create_folder_in_drive(service, folder_name, parent_id=None):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id] if parent_id else [],
        'driveId': SHARED_DRIVE_ID,
    }
    folder = service.files().create(
        body=file_metadata,
        fields='id',
        supportsAllDrives=True
    ).execute()
    return folder.get('id')

def upload_file_to_drive(service, file_path, parent_id):
    file_name = os.path.basename(file_path)
    file_metadata = {
        'name': file_name,
        'parents': [parent_id],
    }
    media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id',
        supportsAllDrives=True
    ).execute()
    print(f"Uploaded {file_name} to Google Drive with ID: {file.get('id')}")

def main():
    # 오늘 날짜 폴더명 (예: 250722)
    today_folder = datetime.datetime.now().strftime('%y%m%d')
    local_folder_path = os.path.join('scheduleData', today_folder)

    if not os.path.exists(local_folder_path):
        print(f"로컬 폴더 {local_folder_path}이(가) 존재하지 않습니다.")
        return

    service = get_drive_service()

    # 공유 드라이브 내 오늘 날짜 폴더 검색
    remote_folder_id = find_folder_in_drive(service, today_folder, parent_id=SHARED_DRIVE_ID)
    if not remote_folder_id:
        print(f"구글 드라이브에 {today_folder} 폴더가 없어서 생성합니다.")
        remote_folder_id = create_folder_in_drive(service, today_folder, parent_id=SHARED_DRIVE_ID)

    # 로컬 폴더 내 파일들 업로드
    for filename in os.listdir(local_folder_path):
        if filename.endswith('.xlsx'):
            local_file_path = os.path.join(local_folder_path, filename)
            upload_file_to_drive(service, local_file_path, remote_folder_id)

if __name__ == '__main__':
    main()
