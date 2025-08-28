#!/usr/bin/env python3
# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : pytest 테스트 실행 스크립트

import subprocess
import sys
import os
import time
from datetime import datetime

def run_tests(test_type="all", additional_args=None):
    """테스트 실행 함수"""
    
    base_cmd = ["python", "-m", "pytest"]
    
    if test_type == "all":
        print("🚀 전체 테스트 실행 중...")
        cmd = base_cmd + ["test/", "-v"]
    
    elif test_type == "main":
        print("🎯 main2_lightweight.py 테스트 실행 중...")
        cmd = base_cmd + ["test/test_main_lightweight.py", "-v"]
    
    elif test_type == "vessel":
        print("🚢 vessel_lists 테스트 실행 중...")
        cmd = base_cmd + ["test/test_vessel_lists.py", "-v"]
    
    elif test_type == "unit":
        print("🔧 단위 테스트만 실행 중...")
        cmd = base_cmd + ["test/", "-m", "unit", "-v"]
    
    elif test_type == "mock":
        print("🎭 모킹 테스트만 실행 중...")
        cmd = base_cmd + ["test/", "-m", "mock", "-v"]
    
    elif test_type == "coverage":
        print("📊 커버리지 포함 테스트 실행 중...")
        cmd = base_cmd + ["test/", "--cov=utils", "--cov-report=html", "-v"]
    
    elif test_type == "fast":
        print("⚡ 빠른 테스트 실행 중...")
        cmd = base_cmd + ["test/", "-x", "--tb=short", "-v"]
    
    elif test_type == "debug":
        print("🐛 디버그 모드로 테스트 실행 중...")
        cmd = base_cmd + ["test/", "-s", "--tb=long", "-v"]
    
    elif test_type == "parallel":
        print("🔄 병렬 테스트 실행 중...")
        cmd = base_cmd + ["test/", "-n", "auto", "-v"]
    
    else:
        print("❌ 잘못된 테스트 타입입니다.")
        return False
    
    # 추가 인자 적용
    if additional_args:
        cmd.extend(additional_args)
    
    print(f"실행 명령: {' '.join(cmd)}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, check=True)
        end_time = time.time()
        duration = end_time - start_time
        
        print("=" * 60)
        print(f"✅ 테스트 완료! (종료 코드: {result.returncode})")
        print(f"⏱️  소요 시간: {duration:.2f}초")
        return True
        
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print("=" * 60)
        print(f"❌ 테스트 실패! (종료 코드: {e.returncode})")
        print(f"⏱️  소요 시간: {duration:.2f}초")
        return False

def run_specific_test(test_file, test_function=None):
    """특정 테스트 파일 또는 함수 실행"""
    if test_function:
        print(f"🎯 {test_file}의 {test_function} 테스트 실행 중...")
        cmd = ["python", "-m", "pytest", f"test/{test_file}::{test_function}", "-v"]
    else:
        print(f"🎯 {test_file} 테스트 실행 중...")
        cmd = ["python", "-m", "pytest", f"test/{test_file}", "-v"]
    
    print(f"실행 명령: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"✅ 테스트 완료! (종료 코드: {result.returncode})")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 테스트 실패! (종료 코드: {e.returncode})")
        return False

def show_test_status():
    """테스트 상태 확인"""
    print("📋 테스트 상태 확인 중...")
    
    # 테스트 파일 존재 여부 확인
    test_files = [
        "test_main_lightweight.py",
        "test_vessel_lists.py"
    ]
    
    print("\n📁 테스트 파일 상태:")
    for test_file in test_files:
        file_path = f"test/{test_file}"
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {test_file} ({file_size:,} bytes)")
        else:
            print(f"❌ {test_file} (파일 없음)")
    
    # pytest 설정 확인
    if os.path.exists("pytest.ini"):
        print("✅ pytest.ini 설정 파일 존재")
    else:
        print("❌ pytest.ini 설정 파일 없음")

def show_help():
    """도움말 표시"""
    print("""
🧪 RPA Crawling Project Test Runner

사용법:
    python run_tests.py [테스트타입] [추가옵션]

테스트 타입:
    all        - 전체 테스트 실행 (기본값)
    main       - main2_lightweight.py 테스트만
    vessel     - vessel_lists 테스트만
    unit       - 단위 테스트만
    mock       - 모킹 테스트만
    coverage   - 커버리지 포함 테스트
    fast       - 빠른 테스트 (첫 실패 시 중단)
    debug      - 디버그 모드 (상세 출력)
    parallel   - 병렬 테스트 실행
    status     - 테스트 상태 확인
    help       - 이 도움말 표시

특정 테스트 실행:
    python run_tests.py specific test_vessel_lists.py
    python run_tests.py specific test_vessel_lists.py test_vessel_lists

추가 옵션:
    --tb=short    - 간단한 에러 출력
    --tb=long     - 상세한 에러 출력
    -x            - 첫 실패 시 중단
    -s            - print 출력 표시
    -k "test_name" - 특정 테스트만 실행

예시:
    python run_tests.py main
    python run_tests.py vessel
    python run_tests.py coverage
    python run_tests.py fast --tb=short
    python run_tests.py specific test_vessel_lists.py
    """)

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        test_type = "all"
        additional_args = None
    else:
        test_type = sys.argv[1].lower()
        additional_args = sys.argv[2:] if len(sys.argv) > 2 else None
    
    # 특별한 명령 처리
    if test_type == "help":
        show_help()
        return
    
    if test_type == "status":
        show_test_status()
        return
    
    if test_type == "specific":
        if len(sys.argv) < 3:
            print("❌ specific 명령어 사용법: python run_tests.py specific <테스트파일> [테스트함수]")
            return
        
        test_file = sys.argv[2]
        test_function = sys.argv[3] if len(sys.argv) > 3 else None
        
        success = run_specific_test(test_file, test_function)
        if success:
            print("\n🎉 특정 테스트가 성공적으로 완료되었습니다!")
        else:
            print("\n💥 특정 테스트가 실패했습니다.")
            sys.exit(1)
        return
    
    print(f"🎯 테스트 타입: {test_type}")
    if additional_args:
        print(f"🔧 추가 옵션: {' '.join(additional_args)}")
    print("=" * 60)
    
    success = run_tests(test_type, additional_args)
    
    if success:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n💥 일부 테스트가 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main() 