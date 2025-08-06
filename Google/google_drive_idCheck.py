from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# 구글 드라이브 파일 권한
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
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
            # client_secret.json 이라는 이름으로 OAuth 클라이언트 시크릿 파일을 준비하세요
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # 토큰 저장
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    # 서비스 객체 생성
    service = build('drive', 'v3', credentials=creds)

    # 업로드할 파일 경로 및 구글 드라이브 폴더 ID
    file_path = 'test.txt'  # 실제 test.txt 경로
    folder_id = '1LDNUDHuVOOgsSxNLeayshu7QiBY5Qh4u'  # 공유 드라이브의 폴더 ID

    # 업로드 메타데이터 (이름, 부모 폴더 설정)
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }

    # 실제 파일 미디어 객체 생성, mimetype은 파일 확장자에 맞게 설정
    media = MediaFileUpload(file_path, mimetype='text/plain')  # test.txt는 일반 텍스트 파일

    # 파일 업로드 요청 실행
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        supportsAllDrives=True,
        fields='id, webViewLink'
        ).execute()

    print(f"파일 업로드 완료: ID={file.get('id')}, 링크={file.get('webViewLink')}")

if __name__ == '__main__':
    main()
