# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/06/30 (완성)
# 선사 링크 : https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel=ㅇㅇIBN%20AL%20ABBAR|IAAB&&func=current&&LocalSite=
# 선박 리스트 : ["YM CREDENTIAL", "YM COOPERATION", "IBN AL ABBAR"]
# 추가 정보 : 순차처리 + 순서 기반 파일명 매핑 사용

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import logging
import traceback

from .base import ParentsClass
import os
import pandas as pd
from datetime import datetime

class YML_Crawling(ParentsClass):
    def __init__(self):
        super().__init__("YML")  # carrier_name을 부모 클래스에 전달
        self.carrier_name = "YML"
        
        # 로깅 설정
        self.setup_logging()
        
        # 선박 리스트
        self.vessel_name_list = ["YM CREDENTIAL", "YM COOPERATION", "IBN AL ABBAR"]
        
        # 선박 코드 매핑
        self.vessel_code = {
            "YM CREDENTIAL": "YCDL",
            "YM COOPERATION": "YCPR",
            "IBN AL ABBAR": "IAAB"
        }
        
        # 크롤링 결과 추적
        self.success_count = 0
        self.fail_count = 0
        self.failed_vessels = []
        self.failed_reasons = {}

    def setup_logging(self):
        """로깅 설정"""
        # 초기에는 에러가 없으므로 파일 로그 생성하지 않음
        self.logger = super().setup_logging(self.carrier_name, has_error=False)
        
    def setup_logging_with_error(self):
        """에러 발생 시 로깅 설정"""
        # 에러가 발생했으므로 파일 로그 생성
        self.logger = super().setup_logging(self.carrier_name, has_error=True)

    def step1_visit_website(self):
        """1단계: 불필요 - step2에서 바로 선박별 접속"""
        try:
            self.logger.info("=== 1단계: 건너뜀 (선박별로 직접 접속) ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 1단계: 오류 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step2_crawl_vessel_data(self):
        """2단계: 지정된 선박별로 루핑 작업 시작"""
        try:
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
            driver = self.driver
            wait = self.wait

            columns = ["Port", "Terminal", "ETA", "ETA-Status", "ETB", "ETB-Status", "ETD", "ETD-Status", "Voy"]

            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_tracking(vessel_name)
                    
                    # 1. 선박별 URL 접속
                    vessel_code = self.vessel_code.get(vessel_name, "")
                    if not vessel_code:
                        self.logger.error(f"선박 {vessel_name}에 대한 코드를 찾을 수 없음")
                        continue
                    
                    vessel_param = vessel_name.replace(" ", "%20")
                    url = f"https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel={vessel_param}|{vessel_code}&&func=current&&LocalSite="
                    self.Visit_Link(url)
                    time.sleep(2)
                    
                    # 2. 쿠키 팝업 있으면 클릭
                    try:
                        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/a')))
                        cookie_button.click()
                        self.logger.info("쿠키 팝업 클릭 완료")
                    except Exception:
                        pass
                    
                    # 3. 항차번호 추출
                    try:
                        voyage_no_elem = wait.until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_lblComn"]'))
                        )
                        voyage_no = voyage_no_elem.text.strip()
                        self.logger.info(f"항차번호 추출: {voyage_no}")
                    except Exception:
                        voyage_no = ""
                        self.logger.warning("항차번호 추출 실패")
                    
                    # 4. 스크롤 Y 100px 내리기
                    driver.execute_script("window.scrollBy(0, 100);")
                    time.sleep(0.5)
                    
                    # 5. 첫 번째 페이지 데이터 추출
                    all_rows = []
                    row_idx = 1
                    while True:
                        xpath = f'//*[@id="ContentPlaceHolder1_gvLast"]/tbody/tr[{row_idx}]'
                        try:
                            tr = driver.find_element(By.XPATH, xpath)
                            tds = tr.find_elements(By.TAG_NAME, "td")
                            row = [td.text.strip() for td in tds]
                            if any(row):  # 빈 행 제거
                                all_rows.append(row)
                            row_idx += 1
                        except Exception:
                            break
                    
                    # 6. 스크롤 Y 100px 올리기
                    driver.execute_script("window.scrollBy(0, -100);")
                    time.sleep(0.5)
                    
                    # 7. 다음 버튼 클릭하여 두 번째 페이지 데이터 수집
                    try:
                        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_btnNext"]')))
                        next_btn.click()
                        time.sleep(1.5)
                        self.logger.info("다음 페이지로 이동 완료")
                        
                        # 두 번째 페이지 데이터도 추가로 수집
                        row_idx = 1
                        while True:
                            xpath = f'//*[@id="ContentPlaceHolder1_gvLast"]/tbody/tr[{row_idx}]'
                            try:
                                tr = driver.find_element(By.XPATH, xpath)
                                tds = tr.find_elements(By.TAG_NAME, "td")
                                row = [td.text.strip() for td in tds]
                                if any(row):  # 빈 행 제거
                                    all_rows.append(row)
                                row_idx += 1
                            except Exception:
                                break
                        
                        self.logger.info("두 번째 페이지 데이터 수집 완료")
                    except Exception as e:
                        self.logger.warning(f"다음 페이지 버튼 없음 또는 클릭 실패: {e}")
                    
                    # 8. DataFrame으로 저장 및 엑셀로 내보내기
                    if all_rows:
                        # 데이터 검증 및 정리
                        cleaned_rows = []
                        for row in all_rows:
                            if row and any(cell.strip() for cell in row if isinstance(cell, str)):
                                cleaned_rows.append(row)
                        
                        if cleaned_rows:
                            df = pd.DataFrame(cleaned_rows)
                            
                            # Port/Terminal/ETA/ETA-Status/ETB/ETB-Status/ETD/ETD-Status 열만 남기고, Voy 칼럼 오른쪽에 추가
                            try:
                                df.drop(columns=[0, 2], inplace=True)
                            except Exception:
                                self.logger.warning("DataFrame drop 실패 - 인덱스를 확인하세요.")
                            
                            df.columns = columns[:-1]
                            df["Voy"] = voyage_no  # 맨 오른쪽 Voy 칼럼
                            
                            # 데이터 타입 정리
                            for col in df.columns:
                                if df[col].dtype == 'object':
                                    df[col] = df[col].astype(str).str.strip()
                            
                            save_path = self.get_save_path(self.carrier_name, vessel_name)
                            
                            try:
                                # openpyxl 엔진으로 저장 (더 안정적)
                                with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                                    df.to_excel(writer, index=False, sheet_name='Schedule Data')
                                
                                self.logger.info(f"[{vessel_name}] 테이블 데이터 저장 완료: {save_path}")
                                self.logger.info(f"저장된 데이터: {len(df)}행 x {len(df.columns)}열")
                                
                                # 파일 크기 확인
                                if os.path.exists(save_path):
                                    file_size = os.path.getsize(save_path)
                                    self.logger.info(f"파일 크기: {file_size / 1024:.2f} KB")
                                
                                # 성공 카운트는 end_vessel_tracking에서 자동 처리됨
                                self.end_vessel_tracking(vessel_name, success=True)
                                vessel_duration = self.get_vessel_duration(vessel_name)
                                self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                                
                            except Exception as excel_error:
                                self.logger.error(f"엑셀 저장 실패: {str(excel_error)}")
                                # 대안: CSV로 저장
                                csv_path = save_path.replace('.xlsx', '.csv')
                                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                                self.logger.info(f"CSV로 대체 저장 완료: {csv_path}")
                                
                                # 성공 처리
                                self.end_vessel_tracking(vessel_name, success=True)
                                vessel_duration = self.get_vessel_duration(vessel_name)
                                self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                        else:
                            self.logger.warning(f"선박 {vessel_name}: 정리된 데이터가 없음")
                            self.end_vessel_tracking(vessel_name, success=False)
                    else:
                        self.logger.warning(f"선박 {vessel_name}: 수집된 데이터가 없음")
                        self.end_vessel_tracking(vessel_name, success=False)
                    
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패: {str(e)}")
                    # 실패한 경우에도 타이머 종료
                    self.end_vessel_tracking(vessel_name, success=False)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                    
                    # 실패한 선박 기록
                    if vessel_name not in self.failed_vessels:
                        self.failed_vessels.append(vessel_name)
                        self.failed_reasons[vessel_name] = str(e)
                    
                    continue
            
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 완료 ===")
            self.logger.info(f"성공: {self.success_count}개, 실패: {self.fail_count}개")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 2단계: 선박별 데이터 크롤링 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def step3_save_with_naming_rules(self):
        """3단계: 파일명 규칙 및 저장경로 규칙 적용"""
        try:
            self.logger.info("=== 3단계: 파일명 규칙 및 저장경로 규칙 적용 시작 ===")
            
            # 기존 파일명 규칙 유지 (선사_선박명.xlsx)
            # 날짜 폴더에 이미 저장되므로 파일명은 변경하지 않음
            self.logger.info("기존 파일명 규칙 유지 (날짜 폴더에 저장됨)")
            
            self.logger.info("=== 3단계: 파일명 규칙 및 저장경로 규칙 적용 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 3단계: 파일명 규칙 및 저장경로 규칙 적용 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False


    def run(self):
        """메인 실행 함수"""
        try:
            self.logger.info("=== YML 크롤링 시작 ===")
            
            # 1단계: 선사 홈페이지 접속
            if not self.step1_visit_website():
                return False
            
            # 2단계: 지정된 선박 리스트 반복해서 조회
            if not self.step2_crawl_vessel_data():
                return False
            
            # 3단계: 파일명 규칙 및 저장경로 규칙 적용
            if not self.step3_save_with_naming_rules():
                return False
            
            # 최종 결과 로깅
            self.logger.info("=== YML 크롤링 완료 ===")
            self.logger.info(f"총 {len(self.vessel_name_list)}개 선박 중")
            self.logger.info(f"성공: {self.success_count}개")
            self.logger.info(f"실패: {self.fail_count}개")
            if self.failed_vessels:
                self.logger.info(f"실패한 선박: {', '.join(self.failed_vessels)}")
            
            self.Close()
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== YML 크롤링 전체 실패 ===")
            self.logger.error(f"에러 메시지: {str(e)}")
            self.logger.error(f"상세 에러: {traceback.format_exc()}")
            return False

    def retry_failed_vessels(self, failed_vessels):
        """
        실패한 선박들에 대해 재시도하는 메서드
        
        Args:
            failed_vessels: 재시도할 선박 이름 리스트
            
        Returns:
            dict: 재시도 결과 (성공/실패 개수 등)
        """
        if not failed_vessels:
            return {
                'retry_success': 0,
                'retry_fail': 0,
                'total_retry': 0,
                'final_success': self.success_count,
                'final_fail': self.fail_count,
                'note': '재시도할 선박이 없습니다.'
            }
        
        self.logger.info(f"=== YML 실패한 선박 재시도 시작 ===")
        self.logger.info(f"재시도 대상 선박: {', '.join(failed_vessels)}")
        self.logger.info(f"재시도 대상 개수: {len(failed_vessels)}개")
        
        # 재시도 전 상태 저장
        original_success_count = self.success_count
        original_fail_count = self.fail_count
        
        # 실패한 선박들만 재시도
        retry_success_count = 0
        retry_fail_count = 0
        
        for vessel_name in failed_vessels:
            try:
                self.logger.info(f"=== {vessel_name} 재시도 시작 ===")
                
                # 선박별 타이머 시작
                self.start_vessel_tracking(vessel_name)
                
                # 1. 선박별 URL 접속
                vessel_code = self.vessel_code.get(vessel_name, "")
                if not vessel_code:
                    self.logger.error(f"선박 {vessel_name}에 대한 코드를 찾을 수 없음")
                    continue
                
                vessel_param = vessel_name.replace(" ", "%20")
                url = f"https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel={vessel_param}|{vessel_code}&&func=current&&LocalSite="
                self.Visit_Link(url)
                time.sleep(2)
                
                # 2. 쿠키 팝업 있으면 클릭
                try:
                    cookie_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/a')))
                    cookie_button.click()
                    self.logger.info("쿠키 팝업 클릭 완료")
                except Exception:
                    pass
                
                # 3. 데이터 테이블 추출
                all_rows = []
                columns = ['Port', 'Terminal', 'ETA', 'ETA-Status', 'ETB', 'ETB-Status', 'ETD', 'ETD-Status', 'Voy']
                
                # 첫 번째 페이지 데이터 추출
                row_idx = 1
                while True:
                    xpath = f'//*[@id="ContentPlaceHolder1_gvLast"]/tbody/tr[{row_idx}]'
                    try:
                        tr = self.driver.find_element(By.XPATH, xpath)
                        tds = tr.find_elements(By.TAG_NAME, "td")
                        row = [td.text.strip() for td in tds]
                        if any(row):  # 빈 행 제거
                            all_rows.append(row)
                        row_idx += 1
                    except Exception:
                        break
                
                # 4. DataFrame으로 저장 및 엑셀로 내보내기
                if all_rows:
                    # 데이터 검증 및 정리
                    cleaned_rows = []
                    for row in all_rows:
                        if row and any(cell.strip() for cell in row if isinstance(cell, str)):
                            cleaned_rows.append(row)
                    
                    if cleaned_rows:
                        df = pd.DataFrame(cleaned_rows)
                        
                        # Port/Terminal/ETA/ETA-Status/ETB/ETB-Status/ETD/ETD-Status 열만 남기고, Voy 칼럼 오른쪽에 추가
                        try:
                            df.drop(columns=[0, 2], inplace=True)
                        except Exception:
                            self.logger.warning("DataFrame drop 실패 - 인덱스를 확인하세요.")
                        
                        df.columns = columns[:-1]
                        df["Voy"] = vessel_name  # 맨 오른쪽 Voy 칼럼
                        
                        save_path = self.get_save_path(self.carrier_name, vessel_name)
                        
                        try:
                            # openpyxl 엔진으로 저장 (더 안정적)
                            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                                df.to_excel(writer, index=False, sheet_name='Schedule Data')
                            
                            self.logger.info(f"{vessel_name} 재시도 테이블 데이터 저장 완료: {save_path}")
                            
                            # 성공 처리
                            retry_success_count += 1
                            
                            # 실패 목록에서 제거
                            if vessel_name in self.failed_vessels:
                                self.failed_vessels.remove(vessel_name)
                            if vessel_name in self.failed_reasons:
                                del self.failed_reasons[vessel_name]
                            
                            self.end_vessel_tracking(vessel_name, success=True)
                            vessel_duration = self.get_vessel_duration(vessel_name)
                            self.logger.info(f"선박 {vessel_name} 재시도 성공 (소요시간: {vessel_duration:.2f}초)")
                            
                        except Exception as excel_error:
                            self.logger.error(f"재시도 엑셀 저장 실패: {str(excel_error)}")
                            # 대안: CSV로 저장
                            csv_path = save_path.replace('.xlsx', '.csv')
                            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                            self.logger.info(f"재시도 CSV로 대체 저장 완료: {csv_path}")
                            
                            # 성공 처리
                            retry_success_count += 1
                            
                            # 실패 목록에서 제거
                            if vessel_name in self.failed_vessels:
                                self.failed_vessels.remove(vessel_name)
                            if vessel_name in self.failed_reasons:
                                del self.failed_reasons[vessel_name]
                            
                            self.end_vessel_tracking(vessel_name, success=True)
                            vessel_duration = self.get_vessel_duration(vessel_name)
                            self.logger.info(f"선박 {vessel_name} 재시도 성공 (소요시간: {vessel_duration:.2f}초)")
                    else:
                        self.logger.warning(f"{vessel_name} 재시도 시에도 정리된 데이터가 없음")
                        retry_fail_count += 1
                        self.end_vessel_tracking(vessel_name, success=False)
                        vessel_duration = self.get_vessel_duration(vessel_name)
                        self.logger.warning(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                        continue
                else:
                    self.logger.warning(f"{vessel_name} 재시도 시에도 데이터가 없음")
                    retry_fail_count += 1
                    self.end_vessel_tracking(vessel_name, success=False)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.warning(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                    continue
                
            except Exception as e:
                self.logger.error(f"선박 {vessel_name} 재시도 실패: {str(e)}")
                retry_fail_count += 1
                
                # 실패한 경우에도 타이머 종료
                self.end_vessel_tracking(vessel_name, success=False)
                vessel_duration = self.get_vessel_duration(vessel_name)
                self.logger.error(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                continue
        
        # 재시도 결과 요약
        self.logger.info("="*60)
        self.logger.info("YML 재시도 결과 요약")
        self.logger.info("="*60)
        self.logger.info(f"재시도 성공: {retry_success_count}개")
        self.logger.info(f"재시도 실패: {retry_fail_count}개")
        self.logger.info(f"재시도 후 최종 성공: {self.success_count}개")
        self.logger.info(f"재시도 후 최종 실패: {self.fail_count}개")
        self.logger.info("="*60)
        
        return {
            'retry_success': retry_success_count,
            'retry_fail': retry_fail_count,
            'total_retry': len(failed_vessels),
            'final_success': self.success_count,
            'final_fail': self.fail_count,
            'final_failed_vessels': self.failed_vessels.copy(),
            'note': f'YML 재시도 완료 - 성공: {retry_success_count}개, 실패: {retry_fail_count}개'
        }
