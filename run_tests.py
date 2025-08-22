#!/usr/bin/env python3
# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : pytest 테스트 실행 스크립트

import subprocess
import sys
import os

def run_tests(test_type="all"):
    """테스트 실행 함수"""
    
    if test_type == "all":
        print("🚀 전체 테스트 실행 중...")
        cmd = ["python", "-m", "pytest", "test/", "-v"]
    
    elif test_type == "main":
        print("🎯 main2_lightweight.py 테스트 실행 중...")
        cmd = ["python", "-m", "pytest", "test/test_main_lightweight.py", "-v"]
    
    elif test_type == "unit":
        print("🔧 단위 테스트만 실행 중...")
        cmd = ["python", "-m", "pytest", "test/", "-m", "unit", "-v"]
    
    elif test_type == "mock":
        print("🎭 모킹 테스트만 실행 중...")
        cmd = ["python", "-m", "pytest", "test/", "-m", "mock", "-v"]
    
    elif test_type == "coverage":
        print("📊 커버리지 포함 테스트 실행 중...")
        cmd = ["python", "-m", "pytest", "test/", "--cov=utils", "--cov-report=html", "-v"]
    
    else:
        print("❌ 잘못된 테스트 타입입니다.")
        return False
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"✅ 테스트 완료! (종료 코드: {result.returncode})")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 테스트 실패! (종료 코드: {e.returncode})")
        return False

def show_help():
    """도움말 표시"""
    print("""
🧪 RPA Crawling Project Test Runner

사용법:
    python run_tests.py [테스트타입]

테스트 타입:
    all        - 전체 테스트 실행 (기본값)
    main       - main2_lightweight.py 테스트만
    unit       - 단위 테스트만
    mock       - 모킹 테스트만
    coverage   - 커버리지 포함 테스트
    help       - 이 도움말 표시

예시:
    python run_tests.py main
    python run_tests.py coverage
    """)

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        test_type = "all"
    else:
        test_type = sys.argv[1].lower()
    
    if test_type == "help":
        show_help()
        return
    
    print(f"🎯 테스트 타입: {test_type}")
    print("=" * 50)
    
    success = run_tests(test_type)
    
    if success:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n💥 일부 테스트가 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main() 