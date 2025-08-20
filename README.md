# RPA 선사 스케줄 크롤링 프로젝트

해운 선사들의 선박 스케줄 데이터를 자동으로 크롤링하고 구글 드라이브에 업로드하는 로직입니다다.
현업의 수기 작업에 오랜 시간이 들어가는것 같아 사이드로 시작된 1인 개발 (크롤링) 입니다.

기술 스택 : Python
디자인 패턴 : 팩토리 메서드
API : 구글 드라이브 API (OAuth 접근 방식)
형상 관리 : Git

## 📋 프로젝트 개요

- **목적**: 해운 선사들의 선박 스케줄 데이터 자동 수집
- **대상 선사**: SITC, EVERGREEN, COSCO, WANHAI, CKLINE 등 15개 선사
- **데이터 형식**: Excel (.xlsx), PDF (.pdf)
- **저장소**: 로컬 → 구글 공유 드라이브 자동 업로드
- **로깅 시스템**: 선사별 개별 로그 + Excel 형태의 통합 로그
- **에러로그 관리**: 자동 구글드라이브 업로드 + 30일 기준 자동 정리

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
├── main.py                    # 메인 실행 파일 (에러로그 자동 업로드 포함)
├── crawler_factory.py         # 크롤러 팩토리 클래스
├── cleanup_old_data.py        # 오래된 데이터 정리 스크립트
├── test_main.py               # 에러로그 업로드 테스트 스크립트
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
Google Drive Upload (스케줄 데이터)
    ↓
Data Cleanup
    ↓
**에러로그 자동 업로드 및 정리**
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

#### 7. **ErrorLog Management (main.py)**
- 오늘 날짜 에러로그 자동 구글드라이브 업로드
- 30일 기준 오래된 에러로그 자동 정리
- 지정된 폴더 ID에 직접 업로드
- 폴더 구조 단순화 (ErrorLog 폴더 생성 불필요)

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

### 6. **에러로그 관리 단계 (ErrorLog Management)**
```
오늘 날짜 로그 → 구글드라이브 업로드 → 30일 이전 로그 → 자동 정리
     ↓                    ↓                    ↓                    ↓
20250120_log.xlsx    지정 폴더 업로드    날짜 기준 스캔    폴더 삭제
     ↓                    ↓                    ↓                    ↓
ErrorLog 폴더     1t3P2oofZKnSrVMmDS6-YQcwuZC6PdCz5    Date Parse    Log Record
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
- **주요 라이브러리**: pandas, openpyxl, google-api-python-client, psutil, concurrent.futures

## 🔧 스레드 안전성 계산기

### 스레드 수 계산 공식

시스템 사양을 분석하여 안전한 스레드 수를 자동으로 계산하는 `thread_calculator.py`를 제공합니다.

#### 1. **메모리 기반 계산**
```python
def calculate_memory_based_threads(self):
    available_memory_gb = self.system_info['memory_available_gb']
    # 크롬 인스턴스당 300MB 필요 (보수적 추정)
    theoretical_threads = available_memory_gb / 0.3
    # 안전 마진 적용 (70%만 사용)
    safe_threads = int(theoretical_threads * 0.7)
    return max(1, min(safe_threads, 8))  # 최소 1개, 최대 8개
```

#### 2. **CPU 기반 계산**
```python
def calculate_cpu_based_threads(self):
    cpu_physical = self.system_info['cpu_physical']
    # 물리적 코어 수의 2배까지 허용 (과부하 방지)
    cpu_based_threads = cpu_physical * 2
    return max(1, min(cpu_based_threads, 6))  # 최소 1개, 최대 6개
```

#### 3. **디스크 기반 계산**
```python
def calculate_disk_based_threads(self):
    disk_free_gb = self.system_info['disk_free_gb']
    # 선사당 약 100MB 필요 (보수적 추정)
    space_per_carrier = 0.1
    theoretical_threads = disk_free_gb / space_per_carrier
    # 안전 마진 적용 (50%만 사용)
    safe_threads = int(theoretical_threads * 0.5)
    return max(1, min(safe_threads, 10))  # 최소 1개, 최대 10개
```

#### 4. **최적 스레드 수 계산**
```python
def get_optimal_thread_count(self):
    memory_threads = self.calculate_memory_based_threads()
    cpu_threads = self.calculate_cpu_based_threads()
    disk_threads = self.calculate_disk_based_threads()
    network_threads = 4  # 네트워크 대역폭 고려
    
    # 가장 보수적인 값 선택 (안전 우선)
    return min(memory_threads, cpu_threads, disk_threads, network_threads)
```

#### 5. **권장 스레드 수 (메모리 기반)**
```python
def get_recommended_thread_count(self):
    memory_total_gb = self.system_info['memory_total_gb']
    
    if memory_total_gb >= 32:
        return 4      # 32GB 이상: 4개 스레드
    elif memory_total_gb >= 16:
        return 3      # 16GB 이상: 3개 스레드
    elif memory_total_gb >= 8:
        return 2      # 8GB 이상: 2개 스레드
    else:
        return 1      # 8GB 미만: 1개 스레드
```

### 사용 예시

```python
# main.py에서 사용
from thread_calculator import ThreadCalculator

calculator = ThreadCalculator()
optimal_threads = calculator.get_optimal_thread_count()

with ThreadPoolExecutor(max_workers=optimal_threads) as executor:
    # 안전한 병렬 처리
    futures = [executor.submit(run_carrier, carrier) 
               for carrier in carriers]
```

### 안전도 평가

- **🟢 매우 안전**: 1-2개 스레드
- **🟡 안전**: 3개 스레드  
- **🟠 주의**: 4개 스레드
- **🔴 위험**: 5-6개 스레드
- **⚫ 매우 위험**: 7개 이상

### 성능 향상 예상치

- **2개 스레드**: 50% 향상 (2배 빠름)
- **3개 스레드**: 67% 향상 (3배 빠름)
- **4개 스레드**: 75% 향상 (4배 빠름)

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

### 에러로그 관리 시스템 도입
- 오늘 날짜 에러로그 자동 구글드라이브 업로드
- 30일 기준 오래된 에러로그 자동 정리
- 지정된 폴더 ID에 직접 업로드로 구조 단순화
- 업로드 성공/실패 상세 추적 및 로깅

### 비동기 처리 방식 도입 (v3.1.0)
- ThreadPoolExecutor를 활용한 스레드 기반 병렬 처리
- 선사별 동시 크롤링으로 성능 향상 (기존 1800초 → 900초 예상)
- 스레드 안전성을 위한 Lock 메커니즘 적용
- 시스템 사양 기반 최적 스레드 수 자동 계산

### 스레드 안전성 및 성능 최적화
- `thread_calculator.py`를 통한 시스템 사양 분석
- 메모리, CPU, 디스크, 네트워크 요소별 안전 스레드 수 계산
- 크롬 인스턴스당 리소스 사용량 고려한 보수적 스레드 수 제한
- 안전도 레벨별 분류 (매우 안전/안전/주의/위험/매우 위험)

## 📝 라이선스

이 프로젝트는 업무 시간 단축으로 도움을 드리고자 사이드로 1인 개발되었습니다.

**마지막 업데이트**: 2025년 1월 20일
**버전**: 3.2.0 