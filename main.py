# 여기서부터 시작함.
from Crawler import base
from Crawler import sitc
from Crawler import evergreen
from Crawler import cosco
from Crawler import wanhai
from Crawler import oocl


if __name__ == "__main__":
    print("Entry Point is Here")
    sitc_data = sitc.SITC_Crawling()
    sitc_data.run()

    # evergreen_data = evergreen.EVERGREEN_Crawling()
    # evergreen_data.run()

    # cosco_data = cosco.Cosco_Crawling()
    # cosco_data.run()

    # wanhai_data = wanhai.WANHAI_Crawling()
    # wanhai_data.run()

    #### oocl은 user-agent써도 CAPTCHA가 있어서 크롤링 보류 #### 
    # oocl_data = oocl.OOCL_Crawling()
    # oocl_data.run()