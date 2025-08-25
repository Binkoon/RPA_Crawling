#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
선박 리스트 매칭 테스트 파일
크롤링 실행 없이 선박 리스트만 확인하는 테스트
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler_factory import CrawlerFactory
from crawler.base import ParentsClass

def test_vessel_list_matching():
    """선박 리스트 매칭 테스트"""
    print("=" * 80)
    print("🚢 선박 리스트 매칭 테스트 시작")
    print("=" * 80)
    
    # 지원되는 모든 선사 목록 가져오기
    supported_carriers = CrawlerFactory.get_all_carrier_names()
    print(f"지원되는 선사 수: {len(supported_carriers)}개")
    print()
    
    # 각 선사별 선박 리스트 테스트
    total_vessels = 0
    success_count = 0
    error_count = 0
    
    for carrier_name in sorted(supported_carriers):
        try:
            print(f"📋 {carrier_name} 테스트 중...")
            
            # 팩토리에서 선박 리스트 가져오기
            factory_vessel_list = CrawlerFactory.get_vessel_list(carrier_name)
            
            # 크롤러 인스턴스 생성하여 직접 선박 리스트 확인
            crawler_instance = CrawlerFactory.create_crawler(carrier_name)
            crawler_vessel_list = getattr(crawler_instance, 'vessel_name_list', [])
            
            # 두 리스트 비교
            if factory_vessel_list == crawler_vessel_list:
                print(f"✅ {carrier_name}: 매칭 성공")
                print(f"   선박 수: {len(crawler_vessel_list)}개")
                print(f"   선박 목록: {crawler_vessel_list}")
                success_count += 1
                total_vessels += len(crawler_vessel_list)
            else:
                print(f"❌ {carrier_name}: 매칭 실패!")
                print(f"   팩토리: {factory_vessel_list}")
                print(f"   크롤러: {crawler_vessel_list}")
                error_count += 1
            
            # 크롤러 인스턴스 정리
            if hasattr(crawler_instance, 'Close'):
                try:
                    crawler_instance.Close()
                except:
                    pass
            
            print()
            
        except Exception as e:
            print(f"❌ {carrier_name}: 오류 발생 - {str(e)}")
            error_count += 1
            print()
    
    # 최종 결과 출력
    print("=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    print(f"총 선사: {len(supported_carriers)}개")
    print(f"성공: {success_count}개")
    print(f"실패: {error_count}개")
    print(f"총 선박 수: {total_vessels}개")
    print(f"성공률: {(success_count/len(supported_carriers)*100):.1f}%")
    
    if error_count == 0:
        print("\n🎉 모든 선사의 선박 리스트가 정상적으로 매칭됩니다!")
    else:
        print(f"\n⚠️  {error_count}개 선사에서 문제가 발생했습니다.")
    
    print("=" * 80)

def test_individual_carrier(carrier_name):
    """개별 선사 선박 리스트 상세 테스트"""
    print(f"\n🔍 {carrier_name} 상세 테스트")
    print("-" * 50)
    
    try:
        # 팩토리에서 선박 리스트 가져오기
        factory_vessel_list = CrawlerFactory.get_vessel_list(carrier_name)
        print(f"팩토리 선박 리스트: {factory_vessel_list}")
        print(f"팩토리 선박 수: {len(factory_vessel_list)}개")
        
        # 크롤러 인스턴스 생성
        crawler_instance = CrawlerFactory.create_crawler(carrier_name)
        crawler_vessel_list = getattr(crawler_instance, 'vessel_name_list', [])
        print(f"크롤러 선박 리스트: {crawler_vessel_list}")
        print(f"크롤러 선박 수: {len(crawler_vessel_list)}개")
        
        # 매칭 확인
        if factory_vessel_list == crawler_vessel_list:
            print("✅ 매칭 성공!")
        else:
            print("❌ 매칭 실패!")
            
        # 크롤러 인스턴스 정리
        if hasattr(crawler_instance, 'Close'):
            try:
                crawler_instance.Close()
            except:
                pass
                
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_factory_methods():
    """팩토리 메서드 테스트"""
    print("\n🔧 팩토리 메서드 테스트")
    print("-" * 50)
    
    try:
        # 지원 선사 확인
        supported = CrawlerFactory.is_supported_carrier('SITC')
        print(f"SITC 지원 여부: {supported}")
        
        # 선사 정보 가져오기
        info = CrawlerFactory.get_carrier_info('SITC')
        print(f"SITC 정보: {info}")
        
        # 총 선박 수
        total = CrawlerFactory.get_total_vessel_count()
        print(f"전체 선박 수: {total}개")
        
        print("✅ 팩토리 메서드 테스트 성공!")
        
    except Exception as e:
        print(f"❌ 팩토리 메서드 테스트 실패: {str(e)}")

def main():
    """메인 테스트 실행"""
    print("🚀 선박 리스트 매칭 테스트 프로그램")
    print("크롤링 실행 없이 선박 리스트만 확인합니다.")
    print()
    
    try:
        # 1. 전체 선사 테스트
        test_vessel_list_matching()
        
        # 2. 팩토리 메서드 테스트
        test_factory_methods()
        
        # 3. 개별 선사 상세 테스트 (선택적)
        print("\n" + "=" * 80)
        print("개별 선사 상세 테스트 (선택사항)")
        print("=" * 80)
        
        test_carriers = ['DYLINE', 'FDT', 'PANOCEAN', 'ONE', 'YML']
        for carrier in test_carriers:
            if CrawlerFactory.is_supported_carrier(carrier):
                test_individual_carrier(carrier)
            else:
                print(f"⚠️  {carrier}는 지원되지 않는 선사입니다.")
        
        print("\n🎯 테스트 완료!")
        
    except Exception as e:
        print(f"\n💥 테스트 실행 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
