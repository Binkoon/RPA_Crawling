# RPA 선사 스케줄 크롤링 프로젝트

해운 선사들의 선박 스케줄 데이터를 자동으로 크롤링하고 구글 드라이브에 업로드하는 RPA 프로젝트입니다.

## 📋 프로젝트 개요

- **목적**: 해운 선사들의 선박 스케줄 데이터 자동 수집
- **대상 선사**: SITC, EVERGREEN, COSCO, WANHAI, CKLINE 등 15개 선사
- **데이터 형식**: Excel (.xlsx), PDF (.pdf)
- **저장소**: 로컬 → 구글 공유 드라이브 자동 업로드

## 🏗️ 프로젝트 구조

```
RPA_Crawling/
├── Google/                    # 구글 드라이브 관련 파일들
│   ├── upload_to_drive_oauth.py    # OAuth 인증 업로드 스크립트
│   ├── upload_to_drive.py          # 서비스 계정 업로드 스크립트
│   ├── first_OAuth.py              # OAuth 인증 설정
│   └── google_drive_idCheck.py     # 드라이브 연결 테스트
├── token/                     # 인증 파일들
│   ├── token.pickle              # OAuth 토큰
│   └── *.json                   # 구글 API 인증 파일들
├── ErrorLog/                  # 에러 로그 (에러 발생 시에만 생성)
│   └── YYYY-MM-DD/             # 날짜별 에러 로그
├── scheduleData/              # 크롤링 데이터 저장소
│   └── YYMMDD/                # 날짜별 데이터 폴더
├── crawler/                   # 크롤러 모듈들
│   ├── base.py                   # 기본 크롤러 클래스
│   ├── sitc.py                   # SITC 크롤러
│   ├── evergreen.py              # EVERGREEN 크롤러
│   ├── cosco.py                  # COSCO 크롤러
│   ├── wanhai.py                 # WANHAI 크롤러
│   ├── ckline.py                 # CKLINE 크롤러
│   ├── panocean.py               # PANOCEAN 크롤러
│   ├── snl.py                    # SNL 크롤러
│   ├── smline.py                 # SMLINE 크롤러
│   ├── hmm.py                    # HMM 크롤러
│   ├── fdt.py                    # FDT 크롤러
│   ├── ial.py                    # IAL 크롤러
│   ├── dyline.py                 # DYLINE 크롤러
│   ├── yml.py                    # YML 크롤러
│   ├── nss.py                    # NSS 크롤러
│   ├── one.py                    # ONE 크롤러
│   └── pil.py                    # PIL 크롤러
├── main.py                    # 메인 실행 파일
├── cleanup_old_data.py        # 오래된 데이터 정리 스크립트
├── main_crawling_log.txt      # 메인 크롤링 로그
└── README.md                  # 프로젝트 설명서
```

## 🚀 설치 및 설정

### 1. 필수 라이브러리 설치

```bash
pip install selenium
pip install pandas
pip install openpyxl
pip install google-auth
pip install google-auth-oauthlib
pip install google-auth-httplib2
pip install google-api-python-client
```

### 2. Chrome WebDriver 설치

- Chrome 브라우저가 설치되어 있어야 합니다
- Selenium이 자동으로 WebDriver를 관리합니다

### 3. 구글 드라이브 API 설정

1. **Google Cloud Console**에서 프로젝트 생성
2. **Google Drive API** 활성화
3. **OAuth 2.0 클라이언트 ID** 생성
4. **서비스 계정 키** 생성 (선택사항)

### 4. 인증 파일 설정

`token/` 폴더에 다음 파일들을 배치:
- `client_secret_*.json` - OAuth 클라이언트 시크릿
- `kmtcrpa-*.json` - 서비스 계정 키 (선택사항)

## 🎯 사용 방법

### 기본 실행

```bash
python main.py
```

### 실행 과정

1. **크롤링 단계**
   - 5개 선사 순차 실행 (SITC, EVERGREEN, COSCO, WANHAI, CKLINE)
   - 각 선사별 선박 스케줄 데이터 수집
   - Excel/PDF 파일로 저장

2. **업로드 단계**
   - 구글 드라이브 OAuth 인증
   - 날짜별 폴더 생성 (예: 250806)
   - 모든 파일 자동 업로드

3. **데이터 정리 단계**
   - 30일 이전 날짜 폴더 자동 삭제
   - 디스크 공간 최적화

4. **결과 요약**
   - 크롤링 성공/실패 통계
   - 업로드 성공/실패 통계
   - 선사별 상세 결과

### 에러 처리

- **에러가 없는 선사**: ErrorLog 폴더에 파일 생성하지 않음
- **에러가 발생한 선사**: `ErrorLog/YYYY-MM-DD/carrierErrorLog.txt` 생성
- **상세 로그**: `main_crawling_log.txt`에 전체 과정 기록

## 📊 지원 선사 목록

| 선사명 | 상태 | 파일 형식 | 선박 수 |
|--------|------|-----------|---------|
| SITC | ✅ 완료 | Excel | 11개 |
| EVERGREEN | ✅ 완료 | Excel | 4개 |
| COSCO | ✅ 완료 | PDF | 4개 |
| WANHAI | ✅ 완료 | Excel | 6개 |
| CKLINE | ✅ 완료 | Excel | 13개 |
| PANOCEAN | ✅ 완료 | Excel | 15개 |
| SNL | ✅ 완료 | Excel | 15개 |
| SMLINE | ✅ 완료 | Excel | 1개 |
| HMM | ✅ 완료 | Excel | 1개 |
| FDT | ✅ 완료 | Excel | 1개 |
| IAL | ✅ 완료 | Excel | 3개 |
| DYLINE | ✅ 완료 | Excel | 3개 |
| YML | ✅ 완료 | Excel | 3개 |
| NSS | ✅ 완료 | Excel | 15개 |
| ONE | 🔄 보완 | Excel | 5개 |

## 🔧 주요 기능

### 1. 자동화된 크롤링
- Selenium WebDriver를 사용한 웹 자동화
- 각 선사별 맞춤형 크롤링 로직
- 에러 발생 시 자동 재시도 및 로깅

### 2. 스마트 에러 처리
- 에러가 없는 선사는 로그 파일 생성하지 않음
- 에러 발생 시에만 상세 로그 기록
- 선사별 개별 에러 처리

### 3. 구글 드라이브 통합
- OAuth 2.0 인증으로 안전한 업로드
- 날짜별 폴더 자동 생성
- 파일 형식별 MIME 타입 자동 설정

### 4. 상세한 결과 보고
- 크롤링 성공/실패 통계
- 업로드 성공/실패 통계
- 선사별 상세 결과
- 실패한 파일 목록

### 5. 자동 데이터 정리
- 30일 이전 날짜 폴더 자동 삭제
- YYMMDD 형식 폴더만 대상 (예: 250606)
- 특수 폴더는 보존 (one_crawling, pil_crawling)
- 디스크 공간 최적화

## 📈 실행 결과 예시

```
=== 크롤링 결과 요약 ===
SITC: 성공 (45.2초)
  └─ 선박: 성공 11개, 실패 0개
EVERGREEN: 성공 (32.1초)
  └─ 선박: 성공 4개, 실패 0개
COSCO: 성공 (28.7초)
  └─ 선박: 성공 4개, 실패 0개

총 5개 선사 중
성공: 5개
실패: 0개
총 소요시간: 156.3초

=== 구글 드라이브 업로드 시작 ===
📁 로컬 폴더: scheduleData/250806
📊 총 파일 수: 82개
🏢 선사 수: 12개

🚀 구글 드라이브 업로드 시작...
Uploaded SITC_SITC DECHENG.xlsx to Google Drive with ID: 1xAxFuoWj4f3a3M8Wrfvyp0QTqXUMVpyV
...

📈 업로드 결과 요약
============================================================
✅ 성공: 82개 파일
❌ 실패: 0개 파일
📊 성공률: 100.0%

🏢 선사별 업로드 결과:
  ✅ SITC: 11/11개 (100.0%)
  ✅ EVERGREEN: 4/4개 (100.0%)
  ✅ COSCO: 4/4개 (100.0%)
  ✅ WANHAI: 6/6개 (100.0%)
  ✅ CKLINE: 13/13개 (100.0%)
============================================================

=== 오래된 데이터 정리 시작 ===
2025-08-06 15:00:27,939 - INFO - === 오래된 데이터 정리 시작 ===
2025-08-06 15:00:27,939 - INFO - 오늘 날짜: 2025-08-06
2025-08-06 15:00:27,940 - INFO - 삭제 기준일: 2025-07-07 (30일 이전)

🗑️ 삭제할 폴더들 (1개):
  - 250606 (2025-06-06)

✅ 삭제 완료: 250606 (2025-06-06)

📊 삭제 결과: 1/1개 폴더 삭제 완료

📁 유지할 폴더들 (11개):
  - 250714 (2025-07-14)
  - 250715 (2025-07-15)
  - 250716 (2025-07-16)
  - 250717 (2025-07-17)
  - 250718 (2025-07-18)
  - 250721 (2025-07-21)
  - 250723 (2025-07-23)
  - 250725 (2025-07-25)
  - 250806 (2025-08-06)
  - one_crawling (특수 폴더)
  - pil_crawling (특수 폴더)

=== 오래된 데이터 정리 완료 ===
```

## 🔒 보안 및 권한

- **OAuth 2.0**: 사용자 인증으로 안전한 API 접근
- **토큰 관리**: `token/` 폴더에 인증 파일 보관
- **에러 로그**: 민감한 정보 제외하고 로그 기록

## 🛠️ 개발 환경

- **Python**: 3.8+
- **Selenium**: 4.0+
- **Chrome**: 최신 버전
- **OS**: Windows 10/11

## 📝 라이선스

이 프로젝트는 내부 사용 목적으로 사이드 과제로 1인 개발되었습니다.

**마지막 업데이트**: 2025년 8월 6일
**버전**: 2.1.0 