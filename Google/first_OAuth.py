from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# 구글 드라이브 파일 업로드 권한 범위
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    creds = None
    # token 폴더 경로 설정
    token_dir = os.path.join(os.getcwd(), 'token')
    token_path = os.path.join(token_dir, 'token.pickle')
    client_secret_path = os.path.join(token_dir, 'client_secret_1_738178615193-mq6bob2pgaejp6ofla52vqhssk9lk14q.apps.googleusercontent.com.json')
    
    # 기존에 인증 토큰이 있으면 불러오기
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    # 토큰이 없거나 만료된 경우 새 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # 새 토큰 저장
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    # 인증된 상태에서 구글 드라이브 서비스 객체 생성(필요 시)
    service = build('drive', 'v3', credentials=creds)
    # 이후, API 호출 가능

if __name__ == '__main__':
    main()
