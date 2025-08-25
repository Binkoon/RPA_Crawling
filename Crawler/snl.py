# # Developer : 디지털전략팀 / 강현빈 사원
# # Date : 2025/06/30 (완성)
# # 선사 링크 : http://eservice.sinotrans.co.kr/eService/es_schedule02.asp?tid=100&sid=2
# # 선박 리스트 : ["AVIOS" , "REN JIAN 27"]
# # 추가 정보 : AVIOS는 지금 안쓰는 선박인거 같음. Phase Out 되었는지 운항팀 확인 필요

# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import Select
# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# import logging
# import traceback

# # 얘는 크롬 안써요  엣지 씁니다 ######
# from selenium.webdriver.edge.options import Options as EdgeOptions
# from selenium.webdriver.edge.service import Service as EdgeService

# from .base import ParentsClass
# import os,re
# import time

# import pandas as pd

# import openpyxl # 얘는 xls로 박아줌.
# import pyexcel

# class SNL_Crawling(ParentsClass):
#     def __init__(self):
#         super().__init__("SNL")
#         self.carrier_name = "SNL"
        
#         # 로깅 설정
#         self.setup_logging()
        
#         # 선박 리스트
#         self.vessel_name_list = ["AVIOS","REN JIAN 27"]
        
#         # 크롤링 결과 추적
#         self.success_count = 0
#         self.fail_count = 0
#         self.failed_vessels = []
#         self.failed_reasons = {}

#         # 기존 드라이버 종료
#         self.driver.quit()

#         # SNL만 해당함!!!!!!!!!!!!! base.py 에다가 등록하면 대참사임
#         # 기존 크롬 드라이버 종료
#         self.driver.quit()
#         # Edge 옵션 설정
#         edge_options = EdgeOptions()
#         edge_options.add_argument("--window-size=1920,1080")
#         self.set_user_agent(edge_options)  # base.py에 이 함수가 크롬/엣지 모두에 적용 가능해야 함
#         edge_options.add_argument("--disable-blink-features=AutomationControlled")
#         edge_options.use_chromium = True
#         edge_options.add_experimental_option("prefs", {
#             "download.default_directory": self.today_download_dir,
#             "download.prompt_for_download": False,
#             "download.directory_upgrade": True,
#             "safebrowsing.enabled": True,
#             "profile.default_content_setting_values.automatic_downloads": 1
#         })

#         # Edge 드라이버로 교체
#         from selenium.webdriver import Edge
#         self.driver = Edge(options=edge_options)
#         self.wait = WebDriverWait(self.driver, 20)

#     def setup_logging(self):
#         """로깅 설정"""
#         # 초기에는 에러가 없으므로 파일 로그 생성하지 않음
#         self.logger = super().setup_logging(self.carrier_name, has_error=False)
        
#     def setup_logging_with_error(self):
#         """에러 발생 시 로깅 설정"""
#         # 에러가 발생했으므로 파일 로그 생성
#         self.logger = super().setup_logging(self.carrier_name, has_error=True)

#     def step1_visit_website(self):
#         """1단계: 선사 홈페이지 접속"""
#         try:
#             self.logger.info("=== 1단계: 선사 홈페이지 접속 시작 ===")
            
#             # 0. 선사 링크 접속
#             self.Visit_Link("http://eservice.sinotrans.co.kr/eService/es_schedule02.asp?tid=100&sid=2")
#             driver = self.driver
#             wait = self.wait
            
#             self.logger.info("=== 1단계: 선사 홈페이지 접속 완료 ===")
#             return True
            
#         except Exception as e:
#             # 에러 발생 시 로깅 설정 변경
#             self.setup_logging_with_error()
#             self.logger.error(f"=== 1단계: 선사 홈페이지 접속 실패 ===")
#             self.logger.error(f"에러 메시지: {str(e)}")
#             self.logger.error(f"상세 에러: {traceback.format_exc()}")
#             return False

#     def step2_crawl_vessel_data(self):
#         """2단계: 지정된 선박별로 루핑 작업 시작"""
#         try:
#             self.logger.info("=== 2단계: 선박별 데이터 크롤링 시작 ===")
            
#             driver = self.driver
#             wait = self.wait

#             # 1. 드랍다운에서 선택해야함
#             select_vessel = driver.find_element(By.XPATH , '//*[@id="vslvoy"]/select')
#             select_vessel_name = Select(select_vessel)

#             for vessel_name in self.vessel_name_list:
#                 try:
#                     self.logger.info(f"선박 {vessel_name} 크롤링 시작")
                    
#                     # 선박별 타이머 시작
#                     self.start_vessel_tracking(vessel_name)
                    
#                     found = False
#                     for option in select_vessel_name.options:
#                         # 옵션 텍스트에 vessel_name이 포함되어 있으면 선택
#                         if vessel_name in option.text:
#                             select_vessel_name.select_by_visible_text(option.text)
#                             self.logger.info(f"선택된 옵션: {option.text}")
#                             found = True
#                             selected_option_text = option.text
#                             break
#                     if not found:
#                         self.logger.warning(f"'{vessel_name}'을(를) 포함하는 옵션이 없습니다.")
#                         self.record_step_failure(vessel_name, "선박 조회", "드롭다운에서 해당 선박을 찾을 수 없음")
#                         continue
                    
#                     search_btn = wait.until(EC.element_to_be_clickable((
#                         By.XPATH , '//*[@id="table12"]/tbody/tr[2]/td[3]/img'
#                     )))
#                     search_btn.click()
#                     time.sleep(1)

#                     table_xpath = '/html/body/table[4]/tbody/tr[1]/td/table/tbody/tr[3]/td/table[2]'
#                     table = driver.find_element(By.XPATH, table_xpath)
#                     rows = table.find_elements(By.TAG_NAME, 'tr')

#                     # th 역할을 하는 첫번째 tr (항상 존재, tr[1])
#                     header_tr = rows[0]
#                     header_cells = header_tr.find_elements(By.TAG_NAME, 'td')
#                     header = [cell.text.strip() for cell in header_cells]

#                     # 만약 데이터 구조가 고정/예측 가능하면 예시처럼 직접 줘도 됩니다:
#                     # header = ['국가', '지역', 'TERMINAL', '입항예정일시', '출항예정일시']

#                     data = []

#                     # 2번째 tr부터, 2씩 증가해서 끝까지(데이터 행만 추출)
#                     for idx in range(1, len(rows), 2):
#                         tr = rows[idx]
#                         tds = tr.find_elements(By.TAG_NAME, 'td')
#                         if not tds:
#                             continue  # 빈 행, 혹은 구조적 결함 패스
#                         values = [td.text.strip() for td in tds]
#                         # 데이터값이 비어 있거나 너무 짧으면 중지
#                         if all([v == "" for v in values]):
#                             continue
#                         data.append(values)

#                     # pandas DataFrame으로 엑셀 저장
#                     import pandas as pd

#                     df = pd.DataFrame(data, columns=header)
#                     formatted_name = selected_option_text  # or vessel_name (원하는 값 기준으로)
#                     save_path = self.get_save_path(self.carrier_name, formatted_name, ext='xlsx')
#                     df.to_excel(save_path, index=False, engine='openpyxl')
#                     self.logger.info(f"파일 저장 완료: {save_path}")
#                     # 성공 카운트는 end_vessel_tracking에서 자동 처리됨
                    
#                     # 선박별 타이머 종료
#                     self.end_vessel_tracking(vessel_name, success=True)
#                     vessel_duration = self.get_vessel_duration(vessel_name)
#                     self.logger.info(f"선박 {vessel_name} 크롤링 완료 (소요시간: {vessel_duration:.2f}초)")
                    
#                 except Exception as e:
#                     self.logger.error(f"선박 {vessel_name} 크롤링 실패: {str(e)}")
#                     # 실패한 경우에도 타이머 종료
#                     self.end_vessel_tracking(vessel_name, success=True)
#                     vessel_duration = self.get_vessel_duration(vessel_name)
#                     self.logger.error(f"선박 {vessel_name} 크롤링 실패 (소요시간: {vessel_duration:.2f}초)")
#                     continue
            
#             self.logger.info("=== 2단계: 선박별 데이터 크롤링 완료 ===")
#             self.logger.info(f"성공: {self.success_count}개, 실패: {self.fail_count}개")
#             return True
            
#         except Exception as e:
#             # 에러 발생 시 로깅 설정 변경
#             self.setup_logging_with_error()
#             self.logger.error(f"=== 2단계: 선박별 데이터 크롤링 실패 ===")
#             self.logger.error(f"에러 메시지: {str(e)}")
#             self.logger.error(f"상세 에러: {traceback.format_exc()}")
#             return False

#     def run(self):
#         """메인 실행 함수"""
#         try:
#             self.logger.info("=== SNL 크롤링 시작 ===")
            
#             # 1단계: 선사 홈페이지 접속
#             if not self.step1_visit_website():
#                 return False
            
#             # 2단계: 지정된 선박별로 루핑 작업 시작
#             if not self.step2_crawl_vessel_data():
#                 return False
            
#             # 최종 결과 로깅
#             self.logger.info("=== SNL 크롤링 완료 ===")
#             self.logger.info(f"총 {len(self.vessel_name_list)}개 선박 중")
#             self.logger.info(f"성공: {self.success_count}개")
#             self.logger.info(f"실패: {self.fail_count}개")
#             if self.failed_vessels:
#                 self.logger.info(f"실패한 선박: {', '.join(self.failed_vessels)}")
            
#             self.Close()
#             return True
            
#         except Exception as e:
#             # 에러 발생 시 로깅 설정 변경
#             self.setup_logging_with_error()
#             self.logger.error(f"=== SNL 크롤링 전체 실패 ===")
#             self.logger.error(f"에러 메시지: {str(e)}")
#             self.logger.error(f"상세 에러: {traceback.format_exc()}")
#             return False

#     def retry_failed_vessels(self, failed_vessels):
#         """
#         실패한 선박들에 대해 재시도하는 메서드
        
#         Args:
#             failed_vessels: 재시도할 선박 이름 리스트
            
#         Returns:
#             dict: 재시도 결과 (성공/실패 개수 등)
#         """
#         if not failed_vessels:
#             return {
#                 'retry_success': 0,
#                 'retry_fail': 0,
#                 'total_retry': 0,
#                 'final_success': self.success_count,
#                 'final_fail': self.fail_count,
#                 'note': '재시도할 선박이 없습니다.'
#             }
        
#         self.logger.info(f"=== SNL 실패한 선박 재시도 시작 ===")
#         self.logger.info(f"재시도 대상 선박: {', '.join(failed_vessels)}")
#         self.logger.info(f"재시도 대상 개수: {len(failed_vessels)}개")
        
#         # 재시도 전 상태 저장
#         original_success_count = self.success_count
#         original_fail_count = self.fail_count
        
#         # 실패한 선박들만 재시도
#         retry_success_count = 0
#         retry_fail_count = 0
        
#         for vessel_name in failed_vessels:
#             try:
#                 self.logger.info(f"=== {vessel_name} 재시도 시작 ===")
                
#                 # 선박별 타이머 시작
#                 self.start_vessel_tracking(vessel_name)
                
#                 # 1. 선박명 입력
#                 vessel_input = self.driver.find_element(By.NAME, 'vessel')
#                 vessel_input.clear()
#                 vessel_input.send_keys(vessel_name)
#                 time.sleep(1)
                
#                 # 2. Search 버튼 클릭
#                 search_btn = self.wait.until(EC.element_to_be_clickable((
#                     By.XPATH, '//*[@id="table12"]/tbody/tr[2]/td[3]/img'
#                 )))
#                 search_btn.click()
#                 time.sleep(1)
                
#                 # 3. 데이터 테이블 추출
#                 table_xpath = '/html/body/table[4]/tbody/tr[1]/td/table/tbody/tr[3]/td/table[2]'
#                 table = self.driver.find_element(By.XPATH, table_xpath)
#                 rows = table.find_elements(By.TAG_NAME, 'tr')
                
#                 # 헤더 추출
#                 header_tr = rows[0]
#                 header_cells = header_tr.find_elements(By.TAG_NAME, 'td')
#                 header = [cell.text.strip() for cell in header_cells]
                
#                 # 데이터 추출
#                 data = []
#                 for idx in range(1, len(rows), 2):
#                     tr = rows[idx]
#                     tds = tr.find_elements(By.TAG_NAME, 'td')
#                     if not tds:
#                         continue
#                     values = [td.text.strip() for td in tds]
#                     if all([v == "" for v in values]):
#                         continue
#                     data.append(values)
                
#                 # 4. DataFrame으로 저장 및 엑셀로 내보내기
#                 if data:
#                     df = pd.DataFrame(data, columns=header)
#                     formatted_name = vessel_name
#                     save_path = self.get_save_path(self.carrier_name, formatted_name, ext='xlsx')
#                     df.to_excel(save_path, index=False, engine='openpyxl')
#                     self.logger.info(f"{vessel_name} 재시도 엑셀 저장 완료: {save_path}")
                    
#                     # 성공 처리
#                     # 성공 카운트는 end_vessel_tracking에서 자동 처리됨
#                     retry_success_count += 1
                    
#                     # 실패 목록에서 제거
#                     if vessel_name in self.failed_vessels:
#                         self.failed_vessels.remove(vessel_name)
#                     if vessel_name in self.failed_reasons:
#                         del self.failed_reasons[vessel_name]
                    
#                     self.end_vessel_tracking(vessel_name, success=True)
#                     vessel_duration = self.get_vessel_duration(vessel_name)
#                     self.logger.info(f"선박 {vessel_name} 재시도 성공 (소요시간: {vessel_duration:.2f}초)")
#                 else:
#                     self.logger.warning(f"{vessel_name} 재시도 시에도 데이터 없음")
#                     retry_fail_count += 1
#                     self.end_vessel_tracking(vessel_name, success=True)
#                     vessel_duration = self.get_vessel_duration(vessel_name)
#                     self.logger.warning(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
                
#             except Exception as e:
#                 self.logger.error(f"선박 {vessel_name} 재시도 실패: {str(e)}")
#                 retry_fail_count += 1
                
#                 # 실패한 경우에도 타이머 종료
#                 self.end_vessel_tracking(vessel_name, success=True)
#                 vessel_duration = self.get_vessel_duration(vessel_name)
#                 self.logger.error(f"선박 {vessel_name} 재시도 실패 (소요시간: {vessel_duration:.2f}초)")
#                 continue
        
#         # 재시도 결과 요약
#         self.logger.info("="*60)
#         self.logger.info("SNL 재시도 결과 요약")
#         self.logger.info("="*60)
#         self.logger.info(f"재시도 성공: {retry_success_count}개")
#         self.logger.info(f"재시도 실패: {retry_fail_count}개")
#         self.logger.info(f"재시도 후 최종 성공: {self.success_count}개")
#         self.logger.info(f"재시도 후 최종 실패: {self.fail_count}개")
#         self.logger.info("="*60)
        
#         return {
#             'retry_success': retry_success_count,
#             'retry_fail': retry_fail_count,
#             'total_retry': len(failed_vessels),
#             'final_success': self.success_count,
#             'final_fail': self.fail_count,
#             'final_failed_vessels': self.failed_vessels.copy(),
#             'note': f'SNL 재시도 완료 - 성공: {retry_success_count}개, 실패: {retry_fail_count}개'
#         }

