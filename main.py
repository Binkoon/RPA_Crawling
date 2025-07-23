# 여기서부터 시작함.
from crawler import base
from crawler import sitc
from crawler import evergreen
from crawler import cosco
from crawler import wanhai
from crawler import one
from crawler import ckline
from crawler import panocean
from crawler import snl
from crawler import smline
from crawler import hmm
from crawler import fdt
from crawler import ial # 완료
from crawler import dyline
from crawler import yml  # 완료
from crawler import pil
from crawler import nss


if __name__ == "__main__":
    print("Entry Point is Here")
    # sitc_data = sitc.SITC_Crawling()
    # sitc_data.run()

    # evergreen_data = evergreen.EVERGREEN_Crawling()
    # evergreen_data.run()

    # cosco_data = cosco.Cosco_Crawling()  # 작업 끝
    # cosco_data.run()

    # wanhai_data = wanhai.WANHAI_Crawling()
    # wanhai_data.run()

    # ckline_data = ckline.CKLINE_Crawling()
    # ckline_data.run()

    # panocean_data = panocean.PANOCEAN_Crawling()
    # panocean_data.run()

    # snl_data = snl.SNL_Crawling()
    # snl_data.run()

    # smline_data = smline.SMLINE_Crawling()
    # smline_data.run()

    # hmm_data = hmm.HMM_Crawling()
    # hmm_data.run()

    # fdt_data = fdt.FDT_Crawling()
    # fdt_data.run()

    # ial_data = ial.IAL_Crawling()
    # ial_data.run()

    # dyline_data = dyline.DYLINE_Crawling()
    # dyline_data.run()

    # yml_data = yml.YML_Crawling()
    # yml_data.run()

    # nss_data = nss.NSS_Crawling()
    # nss_data.run()

    one_data = one.ONE_Crawling()
    one_data.start_crawling()

    # pil_data = pil.PIL_Crawling()
    # pil_data.run()

    

    