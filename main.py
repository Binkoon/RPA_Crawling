# 여기서부터 시작함.
from crawler import base
from crawler import sitc
from crawler import evergreen
from crawler import cosco
from crawler import wanhai
from crawler import oocl
from crawler import one


if __name__ == "__main__":
    print("Entry Point is Here")
    # sitc_data = sitc.SITC_Crawling()   # 현재 스케줄 테이블 엑셀로 추출하는 작업 중
    # sitc_data.run()

    # evergreen_data = evergreen.EVERGREEN_Crawling()
    # evergreen_data.run()

    # cosco_data = cosco.Cosco_Crawling()  # 작업 끝
    # cosco_data.run()

    # wanhai_data = wanhai.WANHAI_Crawling()
    # wanhai_data.run()

    #### oocl은 user-agent써도 CAPTCHA가 있어서 크롤링 보류 #### 
    # oocl_data = oocl.OOCL_Crawling()
    # oocl_data.run()

    one_data = one.ONE_Crawling()
    one_data.run()