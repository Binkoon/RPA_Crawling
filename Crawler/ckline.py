from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from .base import ParentsClass
import time

class CKLINE_Crawling(ParentsClass):
    def __init__(self):
        super().__init__()

    def run(self):
        # 0. 웹사이트 방문
        self.Visit_Link("https://es.ckline.co.kr/")
        driver = self.driver
        wait = self.wait

        # 1. 로딩 화면 대기
        wait.until(EC.invisibility_of_element_located((By.ID, "mf_grp_loading")))

        # 2. 팝업 닫기
        pop_up_close = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mf_btn_noti"]')))
        pop_up_close.click()

        # 3. 스케줄 메뉴 클릭
        menu1 = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div/ul/li[1]')))
        menu1.click()
        time.sleep(0.5)  # 하위 메뉴 표시 대기

        # 4. 선박 메뉴 클릭
        submenu = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div/ul/li[1]/ul/li[2]')))
        submenu.click()
        print("메뉴 클릭 완료!")
        time.sleep(1)  # 페이지 로드 대기 시간 증가

        # 5. 선박별 드롭다운 처리 - 다양한 방법으로 시도
        vessel_name_list = ["SKY MOON"]
        
        # 방법 1: 실제 발견된 ID로 input 요소 찾기
        input_selectors = [
            # 실제 발견된 정확한 ID
            (By.ID, "mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_input"),
            
            # CSS 선택자로 찾기
            (By.CSS_SELECTOR, "input.w2autoComplete_input"),
            (By.CSS_SELECTOR, "input[id*='vessel_input']"),
            (By.CSS_SELECTOR, "input[id*='sbx_vessel']"),
            
            # XPath 다양한 방법
            (By.XPATH, "//input[@id='mf_wfm_intro_tac_layout_contents_WESSCH002_body_sbx_vessel_input']"),
            (By.XPATH, "//input[contains(@id, 'vessel_input')]"),
            (By.XPATH, "//input[contains(@id, 'sbx_vessel')]"),
            (By.XPATH, "//input[@class='w2autoComplete_input']"),
        ]
        
        vessel_input = None
        
        for selector_type, selector in input_selectors:
            try:
                print(f"시도 중: {str(selector_type)} - {selector}")
                
                # 직접 input 찾기
                vessel_input = wait.until(EC.element_to_be_clickable((selector_type, selector)))
                print(f"Input 요소 찾기 성공: {selector}")
                break
                
            except Exception as e:
                print(f"실패: {selector} - {str(e)}")
                continue
        
        if vessel_input is None:
            print("모든 선택자로 input 요소를 찾지 못했습니다.")
            # 디버깅을 위해 페이지 소스 일부 출력
            print("현재 페이지에서 input 요소들:")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i, inp in enumerate(inputs[:10]):  # 처음 10개만
                print(f"Input {i}: id='{inp.get_attribute('id')}', class='{inp.get_attribute('class')}', type='{inp.get_attribute('type')}'")
            self.Close()
            return
        
        # 6. 선박명 입력 및 자동완성 처리
        try:
            for vessel_name in vessel_name_list:
                print(f"선박명 입력 시도: {vessel_name}")
                
                # input 필드 클리어 및 포커스
                vessel_input.clear()
                vessel_input.click()
                time.sleep(0.5)
                
                # 선박명 입력
                vessel_input.send_keys(vessel_name)
                time.sleep(1)  # 자동완성 리스트 로드 대기
                
                # 자동완성 리스트에서 선택
                # 여러 가능한 자동완성 선택자 시도
                autocomplete_selectors = [
                    "//div[contains(@class, 'wAutoComplete_list')]//div[contains(text(), '{}')]".format(vessel_name),
                    "//ul[contains(@class, 'autocomplete')]//li[contains(text(), '{}')]".format(vessel_name),
                    "//div[@class='wAutoComplete_list']//div[text()='{}']".format(vessel_name),
                    "//div[contains(@class, 'dropdown')]//div[contains(text(), '{}')]".format(vessel_name)
                ]
                
                autocomplete_found = False
                for ac_selector in autocomplete_selectors:
                    try:
                        autocomplete_item = wait.until(EC.element_to_be_clickable((By.XPATH, ac_selector)))
                        autocomplete_item.click()
                        print(f"자동완성 선택 성공: {vessel_name}")
                        autocomplete_found = True
                        break
                    except:
                        continue
                
                if not autocomplete_found:
                    # Enter 키로 첫 번째 자동완성 항목 선택 시도
                    vessel_input.send_keys(Keys.ARROW_DOWN)
                    time.sleep(0.2)
                    vessel_input.send_keys(Keys.ENTER)
                    print(f"Enter 키로 자동완성 시도: {vessel_name}")
                
                time.sleep(1)
                
        except Exception as e:
            print(f"선박명 입력 중 오류 발생: {str(e)}")
            self.Close()
            return
        
        print("선박 선택 완료!")

    def debug_page_elements(self):
        """디버깅용: 페이지의 주요 요소들 출력"""
        driver = self.driver
        
        print("=== 페이지 디버깅 정보 ===")
        
        # 모든 input 요소 찾기
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"총 input 요소 개수: {len(inputs)}")
        
        for i, inp in enumerate(inputs):
            print(f"Input {i}:")
            print(f"  - ID: {inp.get_attribute('id')}")
            print(f"  - Class: {inp.get_attribute('class')}")
            print(f"  - Type: {inp.get_attribute('type')}")
            print(f"  - Placeholder: {inp.get_attribute('placeholder')}")
            print(f"  - Visible: {inp.is_displayed()}")
            print("---")
        
        # span 요소들도 확인
        spans = driver.find_elements(By.TAG_NAME, "span")
        autocomplete_spans = [span for span in spans if 'autocomplete' in span.get_attribute('class').lower()]
        print(f"AutoComplete 관련 span 요소: {len(autocomplete_spans)}")
        
        for i, span in enumerate(autocomplete_spans[:5]):  # 처음 5개만
            print(f"Span {i}: class='{span.get_attribute('class')}', text='{span.text}'")