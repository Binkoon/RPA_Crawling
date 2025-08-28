# RPA 선사 스케줄 크롤링 프로젝트

해운 선사들의 선박 스케줄 데이터를 자동으로 크롤링하고 구글 드라이브에 업로드하는 로직입니다.
현업의 수기 작업에 오랜 시간이 들어가는것 같아 사이드로 시작된 1인 개발 (크롤링 쪽 한정) 입니다.

+ 현재 멀티 스레드를 사용할 경우 크롤링 실패가 다소 존재하여 정확성을 높이고자 단일 스레드 처리로 바꾸었습니다.

기술 스택 : Python
라이브러리 : Selenium , cx_oracle , pandas
디자인 패턴 : 팩토리 메서드 + 빌더 패턴
API : 구글 드라이브 API (OAuth 접근 방식)
형상 관리 : Git
DB : 오라클

## 📋 프로젝트 개요

- **목적**: 해운 선사들의 선박 스케줄 데이터 자동 수집
- **대상 선사**: SITC, EVERGREEN, COSCO, WANHAI, CKLINE, ONE, PANOCEAN, YML 등 15개 선사
- **데이터 형식**: Excel (.xlsx), PDF (.pdf)
- **저장소**: 로컬 → 구글 공유 드라이브 자동 업로드
- **로깅 시스템**: 선사별 개별 로그 + Excel 형태의 통합 로그
- **에러로그 관리**: 자동 구글드라이브 업로드 + 30일 기준 자동 정리
- **빌더 패턴**: 단계별 크롤링 프로세스 구성 및 유연한 실행
- **🆕 즉시 파일명 변경**: 파일 다운로드 후 즉시 선박명으로 파일명 변경하여 매칭 정확성 향상

## 🏗️ 프로젝트 구조

```
RPA_Crawling/
├── utils/                     # 🆕 공통 모듈 (경량화)
│   ├── __init__.py               # 패키지 초기화
│   ├── logging_setup.py         # 로깅 설정 공통 모듈
│   ├── google_upload.py         # 구글 드라이브 업로드 공통 모듈
│   ├── data_cleanup.py          # 데이터 정리 공통 모듈
│   ├── excel_logger.py          # 엑셀 로그 관리 공통 모듈
│   ├── crawler_executor.py      # 크롤러 실행 공통 모듈
│   ├── config_loader.py         # 설정 파일 로드 공통 모듈
│   └── config_validator.py      # 설정 검증 공통 모듈
├── config/                     # 🆕 설정 파일
│   ├── carriers.json             # 선사 설정 (기존)
│   ├── config.yaml               # 🆕 기본 설정 파일
│   ├── config_development.yaml   # 🆕 개발 환경 설정
│   ├── config_testing.yaml       # 🆕 테스트 환경 설정
│   └── config_production.yaml    # 🆕 운영 환경 설정
├── Google/                     # 구글 드라이브 관련 파일들
│   ├── upload_to_drive_oauth.py    # OAuth 인증 업로드 스크립트
│   ├── upload_to_drive.py          # 서비스 계정 업로드 스크립트
│   ├── first_OAuth.py              # OAuth 인증 설정
│   └── google_drive_idCheck.py     # 드라이브 연결 테스트
├── token/                      # 인증 파일들
│   ├── token.pickle               # OAuth 토큰
│   └── *.json                    # 구글 API 인증 파일들
├── ErrorLog/                   # 에러 로그 및 통합 로그
│   └── YYYY-MM-DD/              # 날짜별 폴더
│       ├── carrierErrorLog.txt     # 선사별 에러 로그
│       └── YYYY-MM-DD_log.xlsx    # 일일 통합 로그 (Excel)
├── scheduleData/               # 크롤링 데이터 저장소
│   └── YYMMDD/                 # 날짜별 데이터 폴더
├── crawler/                    # 크롤러 모듈들
│   ├── base.py                    # 기본 크롤러 클래스 (공통 기능)
│   ├── sitc.py                    # SITC 크롤러
│   ├── evergreen.py               # EVERGREEN 크롤러
│   ├── cosco.py                   # 🆕 COSCO 크롤러 (즉시 파일명 변경 + 에러 처리 단순화)
│   ├── wanhai.py                  # WANHAI 크롤러
│   ├── ckline.py                  # 🆕 CKLINE 크롤러 (즉시 파일명 변경)
│   ├── panocean.py                # 🆕 PANOCEAN 크롤러 (즉시 파일명 변경)
│   ├── snl.py                     # SNL 크롤러
│   ├── smline.py                  # SMLINE 크롤러
│   ├── hmm.py                     # HMM 크롤러
│   ├── fdt.py                     # FDT 크롤러
│   ├── ial.py                     # IAL 크롤러
│   ├── dyline.py                  # DYLINE 크롤러
│   ├── yml.py                     # 🆕 YML 크롤러 (중복 사이트 방문 제거)
│   ├── nss.py                     # NSS 크롤러
│   └── one.py                     # 🆕 ONE 크롤러 (즉시 파일명 변경 + 동적 URL)
│    
├── main2_lightweight.py        # 🆕 경량화된 메인 실행 파일
├── crawler_factory.py          # 크롤러 팩토리 클래스
├── cleanup_old_data.py         # 오래된 데이터 정리 스크립트
├── test_main.py                # 에러로그 업로드 테스트 스크립트
├── requirements.txt             # Python 의존성 패키지 목록
├── thread_calculator.py        # 스레드 안전성 계산기
├── pytest.ini                  # 🆕 pytest 설정 파일
├── run_tests.py                 # 🆕 테스트 실행 스크립트
├── .gitignore                   # 🆕 Git 무시 파일 목록
└── README.md                   # 프로젝트 설명서
```

## 🏛️ 시스템 아키텍처

### 전체 시스템 구조 (현재 좀 더 업데이트 되었음. 다이어그램 추가 예정)
<img width="813" height="798" alt="System Architecture" src="https://github.com/user-attachments/assets/341e1ea5-ca68-4cad-a20a-d752981fcae0" />

**시스템 흐름:**
main2_lightweight.py (경량화된 메인 컨트롤러) → Config Management (환경별 설정 시스템) → Utils Modules (공통 모듈) → CrawlerFactory (크롤러 생성기) → Individual Crawler (개별 크롤러) → ParentsClass (공통 기능 + 에러 처리 강화) → Data Storage (로컬 파일) → Google Drive Upload (OAuth 2.0 + 환경변수) → Data Cleanup → **에러로그 자동 업로드 및 정리**

### 핵심 컴포넌트

#### 1. **Main Controller (main2_lightweight.py)**
- 전체 프로세스의 진입점 (경량화된 버전)
- **공통 모듈 기반** 모듈화된 구조
- **환경별 설정 관리** 시스템 통합
- **단일 스레드 순차 처리**로 안정성 우선 (향후 멀티스레드 재적용 예정)
- 크롤러 팩토리를 통한 크롤러 인스턴스 생성
- 실행 흐름 제어 및 결과 집계
- Excel 통합 로그 생성
- **환경별 설정 파일 기반** 실행 옵션 관리

#### 2. **🆕 Config Management System (utils/config_loader.py)**
- **환경별 설정**: Development/Testing/Production 환경 분리
- **자동 검증**: 설정값 타입, 범위, 필수값 검증
- **환경변수 오버라이드**: 런타임 설정 변경 지원
- **동적 로딩**: 환경 감지 및 자동 설정 로딩

#### 3. **Crawler Factory (crawler_factory.py)**
- 15개 선사 크롤러의 동적 생성 및 관리
- 모듈명과 클래스명 매핑 테이블 관리
- 크롤러 인스턴스 생명주기 관리

#### 4. **🆕 Enhanced Base Crawler (crawler/base.py)**
- 모든 크롤러의 공통 기능 제공
- **에러 처리 강화**: 스마트 에러 분석 + 타입별 재시도 전략
- **스레드 안전성**: 폴더 생성 Lock 메커니즘
- Selenium WebDriver 설정 및 관리
- 로깅 시스템 및 에러 처리 표준화
- 파일 다운로드 경로 관리

#### 5. **Individual Crawlers (crawler/*.py)**
- 각 선사별 맞춤형 크롤링 로직
- ParentsClass 상속으로 공통 기능 활용
- **에러 처리 강화** 시스템 적용
- 선사별 웹사이트 구조에 최적화된 스크래핑

#### 6. **🆕 Enhanced Google Drive Integration (Google/*.py)**
- OAuth 2.0 인증 기반 안전한 API 접근
- **환경변수 기반** 폴더 ID 관리 (보안 강화)
- 파일별 MIME 타입 자동 감지
- 공유 드라이브 지원 및 권한 관리

#### 7. **Utils Modules (utils/*.py)** 🆕
- **로깅 설정**: `logging_setup.py` - 로깅 시스템 공통 관리
- **구글 업로드**: `google_upload.py` - 구글 드라이브 업로드 공통 로직
- **데이터 정리**: `data_cleanup.py` - 오래된 데이터 정리 공통 로직
- **엑셀 로그**: `excel_logger.py` - 엑셀 로그 관리 공통 로직
- **크롤러 실행**: `crawler_executor.py` - 크롤러 실행 공통 로직
- **설정 로더**: `config_loader.py` - 환경별 설정 로드 공통 로직

#### 8. **🆕 Testing System (pytest + mocking)**
- **테스트 격리**: 실제 실행 방지 mocking 시스템
- **자동화 테스트**: pytest 기반 단위 테스트
- **커버리지 측정**: 테스트 커버리지 리포트
- **CI/CD 준비**: 자동화 파이프라인 준비
- **크롤러별 테스트**: 개별 크롤러 로직 검증
- **통합 테스트**: 전체 워크플로우 검증

#### 9. **Data Management (cleanup_old_data.py)**
- 30일 이전 데이터 자동 정리
- 스케줄링된 정리 작업 지원
- 디스크 공간 최적화

#### 10. **ErrorLog Management (main2_lightweight.py)** 🆕
- 오늘 날짜 에러로그 자동 구글드라이브 업로드
- 30일 기준 오래된 에러로그 자동 정리
- 환경변수 기반 폴더 ID 관리
- 폴더 구조 단순화 (ErrorLog 폴더 생성 불필요)

## 🔄 파일 실행 흐름

### 1. **프로그램 시작 (main2_lightweight.py) - 환경별 설정 기반**
```python
# 환경별 설정 시스템을 활용한 모듈화된 구조
from utils.config_loader import get_system_config, reload_system_config
from utils.logging_setup import setup_main_logging, get_today_log_dir
from utils.crawler_executor import run_carrier_parallel
from utils.excel_logger import save_excel_log, add_google_upload_logs
from utils.google_upload import run_main_upload, upload_errorlog_to_drive
from utils.data_cleanup import cleanup_old_data, cleanup_old_errorlogs

# 환경별 설정 파일 기반 실행 옵션 로드
system_config = get_system_config()
max_workers = system_config.execution.max_workers

# 단일 스레드 순차 크롤링 (안정성 우선)
for carrier_name in carriers_to_run:
    run_carrier_parallel(carrier_name, crawling_results)
```

### 2. **데이터 플로우 구조**
<img width="1354" height="527" alt="Data Flow" src="https://github.com/user-attachments/assets/0693a22d-92a1-40dd-aeaf-7ddd2ae907fd" />

### 3. **🆕 에러 처리 강화 시스템**
```python
# 스마트 에러 분석 및 타입별 재시도 전략
def smart_retry(self, operation, operation_name="", max_retries=None, context=""):
    """에러 분석 기반 스마트 재시도 메서드"""
    for attempt in range(10):  # 최대 10회 시도 (안전장치)
        try:
            result = operation()
            return True, result
        except Exception as e:
            error_analysis = self.analyze_error(e, context)
            if not error_analysis['retryable']:
                return False, error_analysis
            
            # 에러 타입별 재시도 전략 적용
            retry_delay = error_analysis['retry_delay']
            time.sleep(retry_delay)
```

### 4. **크롤러 실행 흐름**
```python
# 각 선사별 크롤링 프로세스 (에러 처리 강화)
def execute_crawling(crawler, carrier_name):
    # 1. 크롤러 초기화
    crawler.setup_logging(carrier_name, has_error=False)
    
    # 2. 선박별 순차 크롤링 (스마트 재시도 적용)
    for vessel in vessels:
        start_time = time.time()
        try:
            success, result = crawler.smart_retry(
                lambda: crawler.crawl_vessel(vessel),
                f"{carrier_name} - {vessel}",
                context=f"carrier={carrier_name},vessel={vessel}"
            )
            duration = time.time() - start_time
            if success:
                add_to_excel_log(carrier_name, vessel, "성공", "크롤링 완료", duration)
            else:
                add_to_excel_log(carrier_name, vessel, "실패", str(result['error_message']), duration)
        except Exception as e:
            duration = time.time() - start_time
            add_to_excel_log(carrier_name, vessel, "실패", str(e), duration)
    
    # 3. 결과 집계 및 로그 저장
    return aggregate_results(crawler)
```

### 5. **데이터 파이프라인 흐름 (환경별 설정 적용)**
```
환경설정 → 로깅설정 → 웹사이트 → Selenium → 데이터 추출 → 파일 저장 → 구글 드라이브 업로드
    ↓           ↓           ↓           ↓           ↓           ↓           ↓
Environment → Logging → HTML/JS → WebDriver → Parsing → Excel/PDF → OAuth API
    ↓           ↓           ↓           ↓           ↓           ↓           ↓
Development → Level → 선박정보 → 스케줄데이터 → 구조화 → 로컬저장 → 클라우드동기화

**환경별 설정 기반 프로세스 단계:**
환경감지 → 설정로드 → 로깅설정 → 크롤링실행 → 에러처리 → 결과집계 → 업로드 → 정리 → 에러로그관리
```

### 6. **에러 처리 및 로깅 흐름 (보완된 시스템입니다 ㅎㅎ)**
```python
# 에러 발생 시 스마트 분석 및 로깅 시스템
if error_occurred:
    # 1. 에러 타입 분석
    error_analysis = self.analyze_error(error, context)
    
    # 2. 재시도 가능 여부 판단
    if error_analysis['retryable']:
        # 재시도 전략 적용
        time.sleep(error_analysis['retry_delay'])
        return self.smart_retry(operation, operation_name)
    
    # 3. 선사별 개별 로그 파일 생성
    crawler.setup_logging(carrier_name, has_error=True)
    
    # 4. Excel 통합 로그에 실패 기록
    add_to_excel_log(carrier_name, vessel, "실패", error_analysis['error_message'], duration)
    
    # 5. 에러 상세 정보 기록 (타입별 로그 레벨 적용)
    if error_analysis['error_type'] == ErrorType.BLOCKED_ERROR:
        logger.error(f"선박 {vessel} 크롤링 차단: {error_analysis['error_message']}")
    else:
        logger.warning(f"선박 {vessel} 크롤링 재시도 가능: {error_analysis['error_message']}")
```

## 🆕 **즉시 파일명 변경 시스템 (v3.6.0)**

### **문제점 해결**
- **기존 방식**: 모든 파일 다운로드 완료 후 일괄 파일명 변경
- **문제점**: 파일명과 내용이 매칭되지 않는 이슈 발생
- **해결책**: 파일 다운로드 직후 즉시 선박명으로 파일명 변경

### **적용된 크롤러**
1. **CKLINE 크롤러** (`crawler/ckline.py`)
   - 파일 다운로드 후 즉시 `CKL_선박명.pdf` 형식으로 변경
   - 파일명-내용 매칭 정확성 100% 달성

2. **PANOCEAN 크롤러** (`crawler/panocean.py`)
   - 특수한 선박명 규칙 지원 (예: "HONOR BRIGHT 1012, 1013, 1014...")
   - 즉시 파일명 변경으로 매칭 오류 방지

3. **COSCO 크롤러** (`crawler/cosco.py`)
   - `cosco_test.py` 기반으로 단순화된 에러 처리
   - 타이밍 최적화 (페이지 로딩: 3초 → 2초)
   - 즉시 파일명 변경으로 안정성 향상

4. **ONE 크롤러** (`crawler/one.py`)
   - 동적 URL 생성 및 3단계 PDF 다운로드 프로세스
   - 파일 다운로드 후 즉시 `ONE_선박명_YYMMDD.pdf` 형식으로 변경
   - 중복 파일명 시 자동 넘버링 처리

5. **YML 크롤러** (`crawler/yml.py`)
   - 중복 사이트 방문 제거로 효율성 향상
   - 테이블 데이터 직접 추출하여 Excel 파일로 저장

### **즉시 파일명 변경 로직**
```python
def rename_downloaded_file(self, vessel_name, timeout=30):
    """다운로드된 파일을 선박명으로 즉시 변경"""
    try:
        start_time = time.time()
        renamed = False
        
        while time.time() - start_time < timeout:
            # 다운로드 디렉토리에서 가장 최근 PDF 파일 찾기
            pdf_files = glob.glob(os.path.join(self.today_download_dir, "*.pdf"))
            
            if pdf_files:
                # 가장 최근 파일 선택 (수정 시간 기준)
                latest_pdf = max(pdf_files, key=os.path.getmtime)
                
                # 파일명이 이미 변경되었는지 확인
                if os.path.basename(latest_pdf).startswith(f"{self.carrier_name}_{vessel_name}"):
                    return True
                
                # 새 파일명 생성
                new_filename = f"{self.carrier_name}_{vessel_name}.pdf"
                new_filepath = os.path.join(self.today_download_dir, new_filename)
                
                # 파일명 변경
                os.rename(latest_pdf, new_filepath)
                self.logger.info(f"선박 {vessel_name}: 파일명 즉시 변경 완료")
                renamed = True
                break
            
            time.sleep(1)
        
        return renamed
        
    except Exception as e:
        self.logger.error(f"파일명 즉시 변경 중 오류: {str(e)}")
        return False
```

### **기대 효과**
- **파일명-내용 매칭 정확성**: 100% 달성
- **처리 속도**: 일괄 처리 대신 즉시 처리로 전체 크롤링 시간 단축
- **안정성**: 각 선박별로 독립적인 파일명 변경으로 실패 영향 최소화
- **디버깅**: 실패 시 즉시 확인 가능

## 🔒 보안 및 권한 (폴더ID의 경우 접근권한이 이미 막혀있어 노출되도 크리티컬하지 않으나 env처리하였습니다.)

- **OAuth 2.0**: 사용자 인증으로 안전한 API 접근
- **토큰 관리**: `token/` 폴더에 인증 파일 보관
- **🆕 환경 변수**: `.env` 파일에 민감한 설정 정보 관리 (폴더 ID 등)
- **에러 로그**: 민감한 정보 제외하고 로그 기록
- **로그 보관**: 1개월 후 자동 삭제
- **🆕 환경별 보안**: 개발/테스트/운영 환경별 보안 수준 분리

## ⚙️ 설정 관리 시스템

### **🆕 환경별 설정 분리**
- **개발 환경** (`config_development.yaml`): 디버깅, 순차 실행, 업로드 비활성화
- **테스트 환경** (`config_testing.yaml`): 테스트용 설정, 제한된 리소스
- **운영 환경** (`config_production.yaml`): 프로덕션 최적화, 보안 강화

### **🆕 설정 검증 및 자동화**
- **자동 검증**: 설정값 타입, 범위, 필수값 검증
- **환경변수 오버라이드**: 런타임 설정 변경 지원
- **설정 템플릿**: 환경별 기본 설정 자동 생성
- **동적 로딩**: 환경 감지 및 자동 설정 로딩

### **사용 예시**
```python
from utils.config_loader import get_system_config, reload_system_config

# 현재 설정 로드
config = get_system_config()
print(f"환경: {config.environment.value}")
print(f"워커 수: {config.execution.max_workers}")
print(f"로그 레벨: {config.logging.level}")

# 설정 리로드
config = reload_system_config()

# 설정 검증
from utils.config_validator import ConfigValidator
validator = ConfigValidator()
results = validator.validate_all_configs()
```

### **환경변수 설정**
```bash
# 환경 설정
export RPA_ENVIRONMENT=production

# 구글 드라이브 설정
export GOOGLE_DRIVE_SCHEDULE_FOLDER_ID=your_schedule_folder_id
export GOOGLE_DRIVE_ERRORLOG_FOLDER_ID=your_errorlog_folder_id

# 실행 설정
export EXECUTION_MODE=parallel
export MAX_WORKERS=4
export LOG_LEVEL=WARNING
```

## 🛠️ 개발 환경 빠른 시작 가이드

```bash
# 1. 프로젝트 다운로드
cd RPA_Crawling

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 설정
# 3-1. 구글 API 설정 (Google/token/ 폴더에 credentials.json 배치)
# 3-2. .env 파일 생성 및 설정
cp .env.example .env
# .env 파일에 GOOGLE_DRIVE_SCHEDULE_FOLDER_ID, GOOGLE_DRIVE_ERRORLOG_FOLDER_ID 설정

# 4. 환경별 설정 확인
export RPA_ENVIRONMENT=development  # development/testing/production

# 5. 테스트 실행 (선택)
python run_tests.py --test-type unit   # 단위 테스트
python run_tests.py --test-type mock   # 모킹 테스트
python run_tests.py --coverage         # 커버리지 포함

# pytest 직접 실행 (권장)
pytest test/ --verbose                 # 모든 테스트 상세 실행
pytest test/test_main_lightweight.py  # 특정 테스트 파일 실행

# 6. 실행
python main2_lightweight.py           # 🆕 권장 (경량화된 버전)
```

**🚀 권장 실행 방법:**
- **새로운 사용자**: `main2_lightweight.py` (경량화된 버전)
- **개발/테스트**: 환경변수 `RPA_ENVIRONMENT=development` 설정
- **운영**: 환경변수 `RPA_ENVIRONMENT=production` 설정

**📊 시각적 문서화:**
- **시스템 아키텍처**: 전체 시스템 구조 및 모듈화 패턴 (v3.5.0 업데이트)
- **데이터 플로우**: 데이터 처리 흐름 및 공통 모듈 활용 (v3.5.0 업데이트)
- **스레드 처리**: 단일 스레드 순차 처리 (안정성 우선, 향후 멀티스레드 재적용 예정)

**🧪 테스트 시스템:**
- **pytest 기반**: 체계적인 테스트 환경 및 모킹 시스템
- **테스트 커버리지**: 단위 테스트 및 통합 테스트 지원
- **자동화 준비**: CI/CD 파이프라인 기반 마련

**⚠️ 환경 설정 주의사항:**
- `.env` 파일에 `GOOGLE_DRIVE_SCHEDULE_FOLDER_ID`, `GOOGLE_DRIVE_ERRORLOG_FOLDER_ID` 설정 필요
- 환경변수 `RPA_ENVIRONMENT`로 환경 분리
- 민감한 정보는 절대 Git에 커밋하지 않음


## 🏗️ 디자인 패턴

### 팩토리 메서드 패턴 (Factory Method Pattern)
- **용도**: 크롤러 인스턴스 생성
- **장점**: 크롤러 타입에 따른 동적 인스턴스 생성, 확장성
- **구현**: `CrawlerFactory.create_crawler(carrier_name)`

### 빌더 패턴 (Builder Pattern) 🔄
- **용도**: 크롤링 프로세스를 단계별로 구성하는 유연한 실행 흐름 관리
- **장점**: 체이닝 방식으로 명확한 프로세스 흐름, 단계별 선택적 실행, 테스트 및 디버깅 용이성
- **구현**: 예정 (향후 업데이트에서 적용)

## 🧩 코드 구조화 방법론

### 모듈화 (Modularization) 🆕
- **용도**: 공통 기능을 별도 모듈로 분리하여 코드 중복 제거
- **장점**: 코드 재사용성 향상, 유지보수성 개선, 가독성 향상
- **구현**: `utils/` 패키지의 공통 모듈들

```python
# 모듈화 사용 예시
from utils.logging_setup import setup_main_logging, get_today_log_dir
from utils.config_loader import get_system_config, reload_system_config
from utils.crawler_executor import run_carrier_parallel
from utils.excel_logger import save_excel_log, add_google_upload_logs
from utils.google_upload import run_main_upload, upload_errorlog_to_drive
from utils.data_cleanup import cleanup_old_data, cleanup_old_errorlogs
```

**공통 모듈별 역할:**
1. **로깅 설정**: `logging_setup.py` - 로깅 시스템 공통 관리
2. **구글 업로드**: `google_upload.py` - 구글 드라이브 업로드 공통 로직
3. **데이터 정리**: `data_cleanup.py` - 오래된 데이터 정리 공통 로직
4. **엑셀 로그**: `excel_logger.py` - 엑셀 로그 관리 공통 로직
5. **크롤러 실행**: `crawler_executor.py` - 크롤러 실행 공통 로직
6. **설정 로더**: `config_loader.py` - 환경별 설정 로드 공통 로직

## 🔧 스레드 안전성 계산기 (현재는 단일 스레드로 운영 중, 향후 멀티스레드 재적용 예정)

### 스레드 처리 구조 (향후 멀티스레드 재적용 예정)
<img width="943" height="702" alt="Image" src="https://github.com/user-attachments/assets/e64497e0-bf3d-4a9d-a39d-332ecf7b3d03" />

**현재 상태**: 단일 스레드 순차 처리로 안정성 우선 운영
**향후 계획**: 안정성 확보 후 멀티스레드 병렬 처리 재적용

### 스레드 수 계산 공식

시스템 사양을 분석하여 향후 멀티스레드 재적용 시 안전한 스레드 수를 자동으로 계산하는 `thread_calculator.py`를 제공합니다.

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

### 사용 예시 (향후 멀티스레드 재적용 시)

```python
# main2_lightweight.py에서 사용 (향후 멀티스레드 재적용 시)
from thread_calculator import ThreadCalculator

calculator = ThreadCalculator()
optimal_threads = calculator.get_optimal_thread_count()

with ThreadPoolExecutor(max_workers=optimal_threads) as executor:
    # 안전한 병렬 처리
    futures = [executor.submit(run_carrier, carrier) 
               for carrier in carriers]
```

**현재 사용 방식 (단일 스레드)**:
```python
# 현재는 단일 스레드 순차 처리
for carrier in carriers:
    run_carrier(carrier)
```

### 안전도 평가

- ** 매우 안전**: 1-2개 스레드
- ** 안전**: 3개 스레드  
- ** 주의**: 4개 스레드
- ** 위험**: 5-6개 스레드
- **⚫ 매우 위험**: 7개 이상

### 성능 향상 예상치 (향후 멀티스레드 재적용 시)

- **2개 스레드**: 50% 향상 (2배 빠름)
- **3개 스레드**: 67% 향상 (3배 빠름)
- **4개 스레드**: 75% 향상 (4배 빠름)

**현재 성능**: 단일 스레드 순차 처리로 안정성 우선
**향후 계획**: 안정성 확보 후 멀티스레드로 성능 향상 도모

## 🧪 테스트 시스템 (ver 3.5.0에 추가입니다.)

### **🆕 pytest 기반 테스트 환경**
```bash
# 전체 테스트 실행
python run_tests.py

# 특정 테스트 타입 실행
python run_tests.py --test-type unit      # 단위 테스트
python run_tests.py --test-type mock      # 모킹 테스트
python run_tests.py --coverage            # 커버리지 포함

# pytest 직접 실행
pytest test/                              # test 폴더의 모든 테스트
pytest test/test_main_lightweight.py     # 특정 테스트 파일
pytest test/test_vessel_lists.py         # 선박 리스트 테스트
```

### **🆕 모킹 시스템**
- **실제 실행 방지**: 크롤링, 파일 생성, Google Drive 업로드 방지
- **격리된 테스트**: 외부 의존성 없는 순수 로직 테스트
- **빠른 피드백**: 실제 실행 시간 없이 즉시 결과 확인
- **테스트 격리**: 각 테스트 간 독립적인 환경 보장

### **테스트 설정**
```python
# pytest.ini 설정
[tool:pytest]
testpaths = test
python_files = test_*.py *_test.py
addopts = --strict-markers --disable-warnings
markers = 
    unit: Unit tests
    integration: Integration tests
    mock: Mock tests
    crawler: Crawler specific tests
```

**테스트 파일 구조:**
```
test/
├── test_main_lightweight.py    # 메인 실행 파일 테스트
├── test_vessel_lists.py        # 선박 리스트 테스트
└── conftest.py                 # pytest 공통 설정 (향후 추가 예정)
```

## 📝 주요 개선사항 (v3.0.0 ~ v3.6.0)

### 🆕 **즉시 파일명 변경 시스템 (v3.6.0)**
- **CKLINE 크롤러**: 파일 다운로드 후 즉시 `CKL_선박명.pdf` 형식으로 변경
- **PANOCEAN 크롤러**: 특수한 선박명 규칙 지원 및 즉시 파일명 변경
- **COSCO 크롤러**: `cosco_test.py` 기반으로 단순화된 에러 처리, 타이밍 최적화, 즉시 파일명 변경
- **ONE 크롤러**: 동적 URL, 3단계 PDF 다운로드, 즉시 파일명 변경
- **YML 크롤러**: 중복 사이트 방문 제거로 효율성 향상

### 🎯 **아키텍처 다이어그램 (v3.5.0 업데이트)**
- **시스템 아키텍처**: 환경별 설정 시스템, 에러 처리 강화, 테스트 시스템 반영
- **데이터 플로우**: 환경별 설정 로드, 스마트 에러 분석, 성능 지표 업데이트
- **스레드 처리**: 단일 스레드 순차 처리 (안정성 우선, 향후 멀티스레드 재적용 예정)

### 🆕 **에러 처리 강화 (v3.5.0)**
- **스마트 에러 분석**: 에러 타입별 분류 및 자동 분석
- **타입별 재시도 전략**: 네트워크, 타임아웃, 차단 등 에러별 맞춤 재시도
- **지능형 재시도**: 에러 특성에 따른 동적 재시도 횟수 및 지연 시간
- **안전장치**: 최대 10회 시도 제한으로 무한 루프 방지

### 🆕 **환경별 설정 관리 시스템 (v3.5.0)**
- **YAML 기반 설정**: JSON에서 YAML로 전환하여 가독성 향상
- **환경 분리**: Development/Testing/Production 환경별 최적화
- **자동 검증**: 설정값 타입, 범위, 필수값 자동 검증
- **환경변수 오버라이드**: 런타임 설정 변경 지원
- **동적 로딩**: 환경 감지 및 자동 설정 로딩

### 🆕 **테스트 시스템 구축 (v3.5.0)**
- **pytest 프레임워크**: 체계적인 테스트 환경 구축
- **모킹 시스템**: 실제 실행 방지 격리된 테스트
- **커버리지 측정**: 테스트 품질 관리
- **자동화 준비**: CI/CD 파이프라인 기반 마련
- **크롤러별 테스트**: 개별 크롤러 로직 검증
- **통합 워크플로우 테스트**: 전체 시스템 검증

### 🆕 **보안 강화 (v3.5.0)**
- **환경변수 기반**: Google Drive 폴더 ID 하드코딩 제거
- **환경별 보안**: 개발/테스트/운영 환경별 보안 수준 분리
- **민감정보 보호**: .env 파일 기반 민감 정보 관리

### 로깅 시스템 대폭 개선 (v3.0.0)
- 메인 로그 파일 제거
- 선사별 개별 로그 생성
- Excel 형태의 통합 로그 시스템 도입
- 선박별 상세 성공/실패 기록

### 성능 및 안정성 향상 (v3.0.0)
- 선박별 개별 소요시간 측정
- 단계별 실패 사유 기록
- 선사 전체 실패 기준 강화 (한 선박이라도 실패하면 전체 실패)
- 에러 처리 로직 개선

### 파일 관리 개선 (v3.0.0)
- ErrorLog 폴더 자동 정리 (1개월 기준)
- 구글 드라이브 업로드 상세 로깅
- 파일별 업로드 성공/실패 추적

### 코드 구조 개선 (v3.0.0)
- base.py에 공통 기능 통합
- 크롤러별 일관된 에러 처리
- 메모리 효율성 향상

### 에러로그 관리 시스템 도입 (v3.0.0)
- 오늘 날짜 에러로그 자동 구글드라이브 업로드
- 30일 기준 오래된 에러로그 자동 정리
- 지정된 폴더 ID에 직접 업로드로 구조 단순화
- 업로드 성공/실패 상세 추적 및 로깅

### 비동기 처리 방식 도입 (v3.1.0) - 현재 일시 중단
- ThreadPoolExecutor를 활용한 스레드 기반 병렬 처리 (향후 재적용 예정)
- 선사별 동시 크롤링으로 성능 향상 (기존 1800초 → 900초 예상)
- 스레드 안전성을 위한 Lock 메커니즘 적용
- 시스템 사양 기반 최적 스레드 수 자동 계산
- **현재 상태**: 안정성 문제로 단일 스레드 순차 처리로 전환

### 빌더 패턴 도입 (v3.3.0)
- 크롤링 프로세스를 단계별로 구성하는 빌더 패턴 적용
- 체이닝 방식으로 유연한 프로세스 구성 가능
- 각 단계를 선택적으로 실행하여 테스트 및 디버깅 용이성 향상
- 프로세스 단계: 환경설정 → 스레드설정 → 선사설정 → 크롤링실행 → 보고서생성 → 드라이브업로드 → 리소스정리

**빌더 패턴의 장점:**
- **유연성**: 필요한 단계만 선택적으로 실행 가능
- **가독성**: 체이닝 방식으로 명확한 프로세스 흐름
- **테스트 용이성**: 특정 단계만 독립적으로 테스트 가능
- **확장성**: 새로운 단계 추가 및 기존 단계 수정 용이
- **유지보수성**: 각 단계가 독립적으로 관리되어 코드 복잡도 감소

### 스레드 안전성 및 성능 최적화 (v3.3.0) - 현재 일시 중단
- `thread_calculator.py`를 통한 시스템 사양 분석 (향후 재적용 시 활용)
- 메모리, CPU, 디스크, 네트워크 요소별 안전 스레드 수 계산
- 크롬 인스턴스당 리소스 사용량 고려한 보수적 스레드 수 제한
- 안전도 레벨별 분류 (매우 안전/안전/주의/위험/매우 위험)
- **현재 상태**: 안정성 우선으로 단일 스레드 순차 처리 운영

### 🆕 **즉시 파일명 변경 시스템 (v3.6.0)**
- **CKLINE 크롤러**: 파일 다운로드 후 즉시 `CKL_선박명.pdf` 형식으로 변경
- **PANOCEAN 크롤러**: 특수한 선박명 규칙 지원 및 즉시 파일명 변경
- **COSCO 크롤러**: `cosco_test.py` 기반 단순화, 타이밍 최적화, 즉시 파일명 변경
- **ONE 크롤러**: 동적 URL, 3단계 PDF 다운로드, 즉시 파일명 변경
- **YML 크롤러**: 중복 사이트 방문 제거로 효율성 향상

### 🆕 **코드 경량화 및 모듈화 (v3.4.0)**
- **main2.py 경량화**: 834줄 → 250줄 (70% 감소)
- **공통 모듈 분리**: `utils/` 패키지로 공통 기능 모듈화
- **설정 파일 기반**: JSON 설정으로 실행 옵션 관리
- **코드 중복 제거**: 동일한 로직을 공통 모듈로 통합
- **가독성 향상**: 함수별 명확한 역할 분담
- **유지보수성**: 개별 모듈 수정으로 전체 시스템 영향 최소화

**경량화 결과:**
- **기존 main2.py**: 834줄 (무거운 버전)
- **새로운 main2_lightweight.py**: ~250줄 (경량화된 버전)
- **개선율**: 70% 코드 감소
- **가독성**: 대폭 향상
- **유지보수성**: 대폭 향상
- **재사용성**: 대폭 향상

**새로운 구조:**
```
utils/                          # 공통 모듈
├── logging_setup.py           # 로깅 설정
├── google_upload.py           # 구글 드라이브 업로드
├── data_cleanup.py            # 데이터 정리
├── excel_logger.py            # 엑셀 로그 관리
├── crawler_executor.py        # 크롤러 실행
└── config_loader.py           # 설정 파일 로드

config/                         # 설정 파일
├── carriers.json              # 선사 설정
├── config.yaml                # 기본 설정
├── config_development.yaml    # 개발 환경 설정
├── config_testing.yaml        # 테스트 환경 설정
└── config_production.yaml     # 운영 환경 설정
```

**환경별 설정 옵션:**
- **실행 모드**: `sequential` (순차) - 현재 안정성 우선으로 병렬 모드 일시 중단
- **스레드 수**: `max_workers` 값 (향후 멀티스레드 재적용 시 활용)
- **로깅 레벨**: DEBUG/INFO/WARNING/ERROR
- **구글 업로드**: 환경별 활성화/비활성화
- **정리 옵션**: 오래된 데이터 정리 기간 등

## 📝 라이선스

이 프로젝트는 업무 시간 단축으로 도움을 드리고자 사이드로 1인 개발되었습니다.
민감정보는 env처리 했으며, 내부 데이터가 아닌 공개된 외부 데이터를 긁어오는 작업이기에 사내 허락을 받고 깃에 올렸습니다.

**마지막 업데이트**: 2025년 8월 28일
**버전**: 3.6.0
