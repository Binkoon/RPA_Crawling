# Developer : 디지털전략팀/강현빈 사원
# Date : 2025/06/30 (완성)
# 선사 링크 : https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel=IBN%20AL%20ABBAR|IAAB&&func=current&&LocalSite=
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
            "YM CREDENTIAL": "YMCR",
            "YM COOPERATION": "YMCO",
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
        """2단계: 지정된 선박 리스트 반복해서 조회"""
        try:
            self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
            driver = self.driver
            wait = self.wait

            for vessel_name in self.vessel_name_list:
                try:
                    self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
                    # 선박별 타이머 시작
                    self.start_vessel_tracking(vessel_name)
                    
                    # 1. 선박별 URL 접속 (첫 번째 선박부터 바로 접속)
                    vessel_code = self.vessel_code.get(vessel_name, "")
                    if not vessel_code:
                        self.logger.error(f"선박 {vessel_name}에 대한 코드를 찾을 수 없음")
                        continue
                    
                    vessel_param = vessel_name.replace(" ", "%20")
                    url = f"https://e-solution.yangming.com/e-service/Vessel_Tracking/vessel_tracking_detail.aspx?vessel={vessel_param}|{vessel_code}&&func=current&&LocalSite="
                    self.Visit_Link(url)
                    time.sleep(2)
                    
                    # 2. 테이블 데이터 추출
                    try:
                        table = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_GridView1"]')))
                        rows = table.find_elements(By.TAG_NAME, "tr")
                        
                        data = []
                        for row in rows[1:]:  # 헤더 제외
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) >= 5:
                                row_data = [cell.text.strip() for cell in cells]
                                data.append(row_data)
                        
                        if data:
                            # 3. DataFrame 생성 및 저장 (올바른 파일명으로 바로 저장)
                            columns = ["Port", "ETA", "ETD", "Status", "Voy"]
                            df = pd.DataFrame(data, columns=columns)
                            
                            # 선박명 추가
                            df.insert(0, "Vessel Name", vessel_name)
                            
                            # 항차번호 추출 (Voy 컬럼에서)
                            if 'Voy' in df.columns:
                                df["Voy"] = df["Voy"].str.extract(r'(\d+)')[0]
                            
                            # 올바른 파일명으로 바로 저장
                            filename = f"{self.carrier_name}_{vessel_name}.xlsx"
                            save_path = os.path.join(self.today_download_dir, filename)
                            df.to_excel(save_path, index=False, header=True)
                            self.logger.info(f"[{vessel_name}] 테이블 데이터 저장 완료: {filename}")
                            
                            # 성공 카운트는 end_vessel_tracking에서 자동 처리됨
                            
                            time.sleep(1)
                            
                            # 선박별 타이머 종료 (성공/실패 카운트 자동 처리)
                            self.end_vessel_tracking(vessel_name, success=True)
                            vessel_duration = self.get_vessel_duration(vessel_name)
                            self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                        else:
                            self.logger.warning(f"선박 {vessel_name}에 대한 데이터가 없습니다.")
                            self.fail_count += 1
                            self.end_vessel_tracking(vessel_name, success=False)
                            
                    except Exception as e:
                        self.logger.error(f"테이블 데이터 추출 실패 ({vessel_name}): {e}")
                        self.end_vessel_tracking(vessel_name, success=False)
                        
                except Exception as e:
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패: {str(e)}")
                    # 실패한 선박 기록 (실패 카운트는 end_vessel_tracking에서 자동 처리됨)
                    
                    # 실패한 경우에도 타이머 종료
                    self.end_vessel_tracking(vessel_name, success=False)
                    vessel_duration = self.get_vessel_duration(vessel_name)
                    self.logger.error(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
                    
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

    def step3_process_downloaded_files(self):
        """3단계: 생성된 파일 확인 및 전처리"""
        try:
            self.logger.info("=== 3단계: 생성된 파일 확인 및 전처리 시작 ===")
            
            # 이미 올바른 파일명으로 저장된 파일들 확인
            expected_files = [f"{self.carrier_name}_{vessel_name}.xlsx" for vessel_name in self.vessel_name_list]
            existing_files = []
            
            for expected_file in expected_files:
                fpath = os.path.join(self.today_download_dir, expected_file)
                if os.path.exists(fpath):
                    existing_files.append(expected_file)
                    self.logger.info(f"파일 확인 완료: {expected_file}")
                else:
                    self.logger.warning(f"예상 파일을 찾을 수 없음: {expected_file}")
            
            # 파일명 변경 후 전처리
            for vessel_name in self.vessel_name_list:
                fpath = os.path.join(self.today_download_dir, f"{self.carrier_name}_{vessel_name}.xlsx")
                if os.path.exists(fpath):
                    try:
                        df = pd.read_excel(fpath)
                        # 1. 'undefined' 컬럼명을 'Vessel Name'으로 변경
                        if 'undefined' in df.columns:
                            df.rename(columns={'undefined': 'Vessel Name'}, inplace=True)
                        # 2. 선박명/항차번호 분리 (첫 컬럼)
                        if 'Vessel Name' in df.columns:
                            split_df = df['Vessel Name'].str.extract(r'(?P<Vessel_Name>[A-Z\s]+)\s+(?P<D_Voy>[A-Z0-9.\-]+)')
                            df['Vessel Name'] = split_df['Vessel_Name']
                            df.insert(1, 'D-Voy', split_df['D_Voy'])

                        # 3. 컬럼명 한글 → 영문 변경
                        col_map = {
                            '지역': 'Port',
                            '입항일': 'ETA',
                            '출항일': 'ETD'
                        }
                        df.rename(columns=col_map, inplace=True)

                        # 4. 컬럼 순서 재정렬
                        desired_cols = ['Vessel Name', 'D-Voy', 'Port', 'ETA', 'ETD']
                        rest_cols = [col for col in df.columns if col not in desired_cols]
                        final_cols = desired_cols + rest_cols
                        df = df[final_cols]

                        # 5. 전처리된 파일로 덮어쓰기
                        df.to_excel(fpath, index=False)
                        self.logger.info(f"전처리 및 컬럼명 변경 완료: {os.path.basename(fpath)}")
                    except Exception as e:
                        self.logger.error(f"전처리 중 오류({vessel_name}): {e}")
                else:
                    self.logger.warning(f"선박 {vessel_name}의 파일을 찾을 수 없음")
            
            # 파일 생성 성공률 계산
            success_rate = (len(existing_files) / len(expected_files)) * 100
            self.logger.info(f"파일 생성 성공률: {success_rate:.1f}% ({len(existing_files)}/{len(expected_files)})")
            
            self.logger.info("=== 3단계: 생성된 파일 확인 및 전처리 완료 ===")
            return True
            
        except Exception as e:
            # 에러 발생 시 로깅 설정 변경
            self.setup_logging_with_error()
            self.logger.error(f"=== 3단계: 생성된 파일 확인 및 전처리 실패 ===")
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
            
            # 3단계: 다운로드된 파일 처리 및 엑셀 생성
            if not self.step3_process_downloaded_files():
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
                
                # 성공 처리 (성공 카운트는 end_vessel_tracking에서 자동 처리됨)
                retry_success_count += 1
                
                # 실패 목록에서 제거
                if vessel_name in self.failed_vessels:
                    self.failed_vessels.remove(vessel_name)
                if vessel_name in self.failed_reasons:
                    del self.failed_reasons[vessel_name]
                
                # 선박별 타이머 종료 (성공/실패 카운트 자동 처리)
                self.end_vessel_tracking(vessel_name, success=True)
                vessel_duration = self.get_vessel_duration(vessel_name)
                self.logger.info(f"선박 {vessel_name} 재시도 성공 (소요시간: {vessel_duration:.2f}초)")
                
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
