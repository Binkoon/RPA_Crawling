from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import file

# API 연결 및 사전정보 입력
store = file.Storage('kmtcrpa-eec~.json') #위에서 받은 OAuth ID Json 파일
creds = store.get()

service = build('drive', 'v3', http=creds.authorize(Http()))

folder_id = "1LDNUDHuVOOgsSxNLeayshu7QiBY5Qh4u" #위에서 복사한 구글드라이브 폴더의 id
file_paths = "test.txt" # 업로드하고자 하는 파일

# 파일을 구글드라이브에 업로드하기
request_body = {'name': file_paths, 'parents': [folder_id], 'uploadType': 'multipart'} # 업로드할 파일의 정보 정의
media = MediaFileUpload(file_paths, mimetype='text/csv') # 업로드할 파일
file_info = service.files().create(body=request_body,media_body=media, fields='id,webViewLink').execute()