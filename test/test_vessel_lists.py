#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
선박 리스트 매칭 테스트 파일 (pytest용)
크롤링 실행 없이 선박 리스트만 확인하는 테스트
"""

import pytest
from crawler_factory import CrawlerFactory

def test_vessel_lists():
    """선박 리스트가 올바르게 매칭되는지 테스트"""
    # SMLINE과 SNL을 제외한 모든 선사 테스트
    
    # DYLINE
    dyline_vessels = CrawlerFactory.get_vessel_list('DYLINE')
    expected_dyline = ["PEGASUS TERA", "PEGASUS HOPE", "PEGASUS PETA"]
    assert dyline_vessels == expected_dyline, f"DYLINE: {dyline_vessels}"
    
    # FDT
    fdt_vessels = CrawlerFactory.get_vessel_list('FDT')
    expected_fdt = ["SHIMIN"]
    assert fdt_vessels == expected_fdt, f"FDT: {fdt_vessels}"
    
    # PANOCEAN
    panocean_vessels = CrawlerFactory.get_vessel_list('PANOCEAN')
    expected_panocean = ["POS SINGAPORE", "HONOR BRIGHT", "POS QINGDAO", "POS GUANGZHOU", "POS HOCHIMINH", "POS LAEMCHABANG"]
    assert panocean_vessels == expected_panocean, f"PANOCEAN: {panocean_vessels}"
    
    # ONE
    one_vessels = CrawlerFactory.get_vessel_list('ONE')
    expected_one = ["MARIA C", "ONE REASSURANCE", "ST SUCCESS", "ONE MAJESTY"]
    assert one_vessels == expected_one, f"ONE: {one_vessels}"
    
    # YML
    yml_vessels = CrawlerFactory.get_vessel_list('YML')
    expected_yml = ["YM CREDENTIAL", "YM COOPERATION", "YM INITIATIVE"]
    assert yml_vessels == expected_yml, f"YML: {yml_vessels}"
    
    # SITC
    sitc_vessels = CrawlerFactory.get_vessel_list('SITC')
    expected_sitc = ["SITC XIN", "SITC YUNCHENG", "SITC MAKASSAR", "SITC CHANGDE", "SITC HANSHIN", "SITC XINGDE", "AMOUREUX"]
    assert sitc_vessels == expected_sitc, f"SITC: {sitc_vessels}"
    
    # EVERGREEN
    evergreen_vessels = CrawlerFactory.get_vessel_list('EVERGREEN')
    expected_evergreen = ["EVER GIVEN", "EVER GOOD", "EVER GRADE"]
    assert evergreen_vessels == expected_evergreen, f"EVERGREEN: {evergreen_vessels}"
    
    # COSCO
    cosco_vessels = CrawlerFactory.get_vessel_list('COSCO')
    expected_cosco = ["XIN NAN SHA", "XIN RI ZHAO", "XIN WU HAN", "XIN SU ZHOU", "COSCO HAIFA", "XIN QIN HUANG DAO", "XIN TIAN JIN", "PHEN BASIN", "XIN YAN TIAN", "XIN NING BO", "TIAN CHANG HE"]
    assert cosco_vessels == expected_cosco, f"COSCO: {cosco_vessels}"
    
    # WANHAI
    wanhai_vessels = CrawlerFactory.get_vessel_list('WANHAI')
    expected_wanhai = ["WAN HAI 101", "WAN HAI 102", "WAN HAI 103", "WAN HAI 104", "WAN HAI 105", "WAN HAI 106", "WAN HAI 107"]
    assert wanhai_vessels == expected_wanhai, f"WANHAI: {wanhai_vessels}"
    
    # CKLINE
    ckline_vessels = CrawlerFactory.get_vessel_list('CKLINE')
    expected_ckline = ["SKY MOON", "SKY FLOWER", "SKY JADE", "SKY TIARA", "SUNWIN", "SKY VICTORIA", "VICTORY STAR", "SKY IRIS", "SKY SUNSHINE", "SKY RAINBOW", "BAL BOAN", "SKY CHALLENGE", "XIN TAI PING", "SKY ORION"]
    assert ckline_vessels == expected_ckline, f"CKLINE: {ckline_vessels}"
    
    # HMM
    hmm_vessels = CrawlerFactory.get_vessel_list('HMM')
    expected_hmm = ["HMM BANGKOK"]
    assert hmm_vessels == expected_hmm, f"HMM: {hmm_vessels}"
    
    # IAL
    ial_vessels = CrawlerFactory.get_vessel_list('IAL')
    expected_ial = ["INTERASIA PROGRESS", "INTERASIA ENGAGE", "INTERASIA HORIZON"]
    assert ial_vessels == expected_ial, f"IAL: {ial_vessels}"
    
    # NSS
    nss_vessels = CrawlerFactory.get_vessel_list('NSS')
    expected_nss = ["STARSHIP JUPITER", "STAR CHALLENGER", "STAR PIONEER", "PEGASUS GRACE", "STAR FRONTIER", "STAR SKIPPER", "STARSHIP MERCURY", "STARSHIP TAURUS", "STARSHIP DRACO", "STARSHIP URSA", "STAR CLIPPER", "STAR EXPRESS", "STARSHIP AQUILA", "STAR CHASER", "STAR RANGER", "STARSHIP PEGASUS", "STAR EXPLORER"]
    assert nss_vessels == expected_nss, f"NSS: {nss_vessels}"
    
    print("✅ 모든 선사의 선박 리스트가 정상적으로 매칭됩니다!")
