# RPA 선사 스케줄 크롤링 프로젝트

해운 선사들의 선박 스케줄 데이터를 자동으로 크롤링하고 구글 드라이브에 업로드하는 RPA 프로젝트입니다.

## 📋 프로젝트 개요

- **목적**: 해운 선사들의 선박 스케줄 데이터 자동 수집
- **대상 선사**: SITC, EVERGREEN, COSCO, WANHAI, CKLINE 등 15개 선사
- **데이터 형식**: Excel (.xlsx), PDF (.pdf)
- **저장소**: 로컬 → 구글 공유 드라이브 자동 업로드
- **로깅 시스템**: 선사별 개별 로그 + Excel 형태의 통합 로그

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
├── ErrorLog/                  # 에러 로그 및 통합 로그
│   └── YYYY-MM-DD/             # 날짜별 폴더
│       ├── carrierErrorLog.txt    # 선사별 에러 로그
│       └── YYYY-MM-DD_log.xlsx   # 일일 통합 로그 (Excel)
├── scheduleData/              # 크롤링 데이터 저장소
│   └── YYMMDD/                # 날짜별 데이터 폴더
├── crawler/                   # 크롤러 모듈들
│   ├── base.py                   # 기본 크롤러 클래스 (공통 기능)
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
├── crawler_factory.py         # 크롤러 팩토리 클래스
├── cleanup_old_data.py        # 오래된 데이터 정리 스크립트
└── README.md                  # 프로젝트 설명서
```

## 🏛️ 시스템 아키텍처

### 전체 시스템 구조
main.py (메인 컨트롤러)
    ↓
CrawlerFactory (크롤러 생성기)
    ↓
Individual Crawler (개별 크롤러)
    ↓
ParentsClass (공통 기능)
    ↓
Data Storage (로컬 파일)
    ↓
Google Drive Upload
    ↓
Data Cleanup
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main Entry    │───▶│  Crawler        │───▶│  Data Storage   │
│   (main.py)     │    │  Factory        │    │  (Local Files)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Individual     │    │  Base Crawler   │    │  Google Drive   │
│  Crawlers       │    │  (base.py)      │    │  Upload         │
│  (15 carriers)  │    │                 │    │  (OAuth/API)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Error Logging  │    │  Data Pipeline  │    │  Cleanup        │
│  System         │    │  Management     │    │  (Auto)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 핵심 컴포넌트

#### 1. **Main Controller (main.py)**
- 전체 프로세스의 진입점
- 크롤러 팩토리를 통한 크롤러 인스턴스 생성
- 실행 흐름 제어 및 결과 집계
- Excel 통합 로그 생성

#### 2. **Crawler Factory (crawler_factory.py)**
- 15개 선사 크롤러의 동적 생성 및 관리
- 모듈명과 클래스명 매핑 테이블 관리
- 크롤러 인스턴스 생명주기 관리

#### 3. **Base Crawler (crawler/base.py)**
- 모든 크롤러의 공통 기능 제공
- Selenium WebDriver 설정 및 관리
- 로깅 시스템 및 에러 처리 표준화
- 파일 다운로드 경로 관리

#### 4. **Individual Crawlers (crawler/*.py)**
- 각 선사별 맞춤형 크롤링 로직
- ParentsClass 상속으로 공통 기능 활용
- 선사별 웹사이트 구조에 최적화된 스크래핑

#### 5. **Google Drive Integration (Google/*.py)**
- OAuth 2.0 인증 기반 안전한 API 접근
- 파일별 MIME 타입 자동 감지
- 공유 드라이브 지원 및 권한 관리

#### 6. **Data Management (cleanup_old_data.py)**
- 30일 이전 데이터 자동 정리
- 스케줄링된 정리 작업 지원
- 디스크 공간 최적화

## 🔄 파일 실행 흐름

### 1. **프로그램 시작 (main.py)**
```python
# 1. 환경 설정 및 폴더 구조 생성
setup_errorlog_folder()           # ErrorLog 폴더 생성
load_carriers_config()            # 선사 설정 로드

# 2. 크롤러 팩토리 초기화
crawler_factory = CrawlerFactory()

# 3. 선사별 크롤링 실행
for carrier_name in carrier_names:
    crawler = crawler_factory.create_crawler(carrier_name)
    result = execute_crawling(crawler, carrier_name)
```

### 2. **크롤러 실행 흐름**
```python
# 각 선사별 크롤링 프로세스
def execute_crawling(crawler, carrier_name):
    # 1. 크롤러 초기화
    crawler.setup_logging(carrier_name, has_error=False)
    
    # 2. 선박별 순차 크롤링
    for vessel in vessels:
        start_time = time.time()
        try:
            result = crawler.crawl_vessel(vessel)
            duration = time.time() - start_time
            add_to_excel_log(carrier_name, vessel, "성공", "크롤링 완료", duration)
        except Exception as e:
            duration = time.time() - start_time
            add_to_excel_log(carrier_name, vessel, "실패", str(e), duration)
    
    # 3. 결과 집계 및 로그 저장
    return aggregate_results(crawler)
```

### 3. **데이터 파이프라인 흐름**
```
웹사이트 → Selenium → 데이터 추출 → 파일 저장 → 구글 드라이브 업로드
   ↓           ↓           ↓           ↓           ↓
HTML/JS → WebDriver → Parsing → Excel/PDF → OAuth API
   ↓           ↓           ↓           ↓           ↓
선박정보 → 스케줄데이터 → 구조화 → 로컬저장 → 클라우드동기화
```

### 4. **에러 처리 및 로깅 흐름**
```python
# 에러 발생 시 로깅 시스템
if error_occurred:
    # 1. 선사별 개별 로그 파일 생성
    crawler.setup_logging(carrier_name, has_error=True)
    
    # 2. Excel 통합 로그에 실패 기록
    add_to_excel_log(carrier_name, vessel, "실패", error_message, duration)
    
    # 3. 에러 상세 정보 기록
    logger.error(f"선박 {vessel} 크롤링 실패: {error_message}")
```

## 📊 데이터 파이프라인

### 1. **데이터 수집 단계 (Collection)**
```
웹사이트 접속 → 로그인/인증 → 선박 목록 조회 → 개별 선박 상세 정보
     ↓              ↓              ↓              ↓
  Selenium      Cookie/Token    HTML Parsing   Data Extraction
     ↓              ↓              ↓              ↓
  WebDriver     Session Mgmt    DOM Traversal  Structured Data
```

### 2. **데이터 처리 단계 (Processing)**
```
원시 데이터 → 데이터 정제 → 형식 변환 → 파일 생성
     ↓            ↓            ↓            ↓
HTML/Text    Validation    Standardize   Excel/PDF
     ↓            ↓            ↓            ↓
Parsing      Error Check   Formatting    File Output
```

### 3. **데이터 저장 단계 (Storage)**
```
로컬 저장 → 폴더 구조화 → 메타데이터 생성 → 백업
     ↓            ↓            ↓            ↓
scheduleData  YYMMDD/      File Info     ErrorLog
     ↓            ↓            ↓            ↓
Excel/PDF    Date-based    Timestamp    Audit Trail
```

### 4. **데이터 동기화 단계 (Sync)**
```
로컬 파일 → 구글 드라이브 → 권한 설정 → 공유 설정
     ↓            ↓            ↓            ↓
File Check   OAuth Auth    MIME Type    Drive ID
     ↓            ↓            ↓            ↓
Validation   API Upload    Metadata     Access Control
```

### 5. **데이터 정리 단계 (Cleanup)**
```
30일 경과 → 폴더 스캔 → 삭제 대상 식별 → 자동 정리
     ↓            ↓            ↓            ↓
Time Check   Directory    Date Parse    File Remove
     ↓            ↓            ↓            ↓
Cutoff Date  Scan All     Validation   Log Record
```

## 🔧 주요 기능

### 1. 자동화된 크롤링
- Selenium WebDriver를 사용한 웹 자동화
- 각 선사별 맞춤형 크롤링 로직
- 에러 발생 시 자동 재시도 및 로깅
- 선박별 개별 소요시간 측정

### 2. 스마트 에러 처리
- 에러가 없는 선사는 로그 파일 생성하지 않음
- 에러 발생 시에만 상세 로그 기록
- 선사별 개별 에러 처리
- 단계별 실패 사유 기록 (예: "선박 조회 실패", "데이터 없음")

### 3. 고급 로깅 시스템
- **선사별 개별 로그**: 각 크롤러의 상세 실행 로그
- **Excel 통합 로그**: 일일 크롤링 결과를 Excel 형태로 저장
- **선박별 상세 기록**: 성공/실패, 소요시간, 실패 사유 등
- **요약 통계**: 총 선사 수, 성공/실패 수, 총 소요시간 등

### 4. 구글 드라이브 통합
- OAuth 2.0 인증으로 안전한 API 접근
- 날짜별 폴더 자동 생성
- 파일 형식별 MIME 타입 자동 설정
- 업로드 성공/실패 상세 로깅

### 5. 자동 데이터 정리
- 30일 이전 날짜 폴더 자동 삭제
- ErrorLog 폴더도 1개월 기준으로 정리
- YYMMDD 형식 폴더만 대상 (예: 250606)
- 특수 폴더는 보존 (one_crawling, pil_crawling)

### 6. 선박별 성공/실패 추적
- 각 선박의 크롤링 성공/실패 개별 기록
- 선박별 소요시간 측정 (루프 시작부터 완료까지)
- 실패한 선박이 있으면 해당 선사 전체를 실패로 처리
- 상세한 실패 사유 기록

## 📈 실행 결과 예시

### 크롤링 결과 요약
```
=== 크롤링 결과 요약 ===
SITC: 성공 (45.2초)
  └─ 선박: 성공 11개, 실패 0개
EVERGREEN: 성공 (32.1초)
  └─ 선박: 성공 4개, 실패 0개
COSCO: 성공 (28.7초)
  └─ 선박: 성공 4개, 실패 0개

총 15개 선사 중
성공: 15개
실패: 0개
총 소요시간: 156.3초

=== 선박별 상세 결과 ===
총 선박: 88개
성공: 88개
실패: 0개
```

### 구글 드라이브 업로드 결과
```
=== 구글 드라이브 업로드 시작 ===
📁 로컬 폴더: scheduleData/250806
📊 총 파일 수: 82개
🏢 선사 수: 15개

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
```

### Excel 로그 파일 구조
```
날짜 (Y/M/D/HH/MM/SS) | 선사 | 선박 | 상태 | 사유/결과 | 소요시간
2025/08/06/15/00/27   | SITC | SITC DECHENG | 성공 | 크롤링 완료 | 4.2초
2025/08/06/15/00/31   | SITC | SITC DECHENG | 성공 | 크롤링 완료 | 3.8초
...

=== 크롤링 결과 요약 ===
총 15개 선사 중
성공: 15개
실패: 0개
총 소요시간: 156.3초

=== 선박별 상세 결과 ===
총 선박: 88개
성공: 88개
실패: 0개
```

## 🔒 보안 및 권한

- **OAuth 2.0**: 사용자 인증으로 안전한 API 접근
- **토큰 관리**: `token/` 폴더에 인증 파일 보관
- **에러 로그**: 민감한 정보 제외하고 로그 기록
- **로그 보관**: 1개월 후 자동 삭제

## 🛠️ 개발 환경

- **Python**: 3.8+
- **Selenium**: 4.0+
- **Chrome**: 최신 버전
- **OS**: Windows 10/11
- **주요 라이브러리**: pandas, openpyxl, google-api-python-client

## 📝 주요 개선사항 (v3.0.0)

### 로깅 시스템 대폭 개선
- 메인 로그 파일 제거
- 선사별 개별 로그 생성
- Excel 형태의 통합 로그 시스템 도입
- 선박별 상세 성공/실패 기록

### 성능 및 안정성 향상
- 선박별 개별 소요시간 측정
- 단계별 실패 사유 기록
- 선사 전체 실패 기준 강화 (한 선박이라도 실패하면 전체 실패)
- 에러 처리 로직 개선

### 파일 관리 개선
- ErrorLog 폴더 자동 정리 (1개월 기준)
- 구글 드라이브 업로드 상세 로깅
- 파일별 업로드 성공/실패 추적

### 코드 구조 개선
- base.py에 공통 기능 통합
- 크롤러별 일관된 에러 처리
- 메모리 효율성 향상

## 📝 라이선스

이 프로젝트는 내부 사용 목적으로 사이드 과제로 1인 개발되었습니다.

**마지막 업데이트**: 2025년 8월 19일
**버전**: 3.0.0 