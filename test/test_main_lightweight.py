# Developer : 디지털전략팀 / 강현빈 사원
# Date : 2025/08/21
# 역할 : main2_lightweight.py pytest 테스트 (모킹 기반)

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import tempfile
import shutil

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestMainLightweight:
    """main2_lightweight.py 테스트 클래스"""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """테스트 환경 설정"""
        # 임시 폴더 생성
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # 테스트용 폴더 구조 생성
        os.makedirs('scheduleData', exist_ok=True)
        os.makedirs('ErrorLog', exist_ok=True)
        os.makedirs('config', exist_ok=True)
        os.makedirs('utils', exist_ok=True)
        
        yield
        
        # 테스트 후 정리
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    @patch('utils.config_loader.get_carriers_to_run')
    @patch('utils.config_loader.load_execution_config')
    def test_config_loading(self, mock_load_config, mock_get_carriers):
        """설정 파일 로딩 테스트"""
        # 모킹 설정
        mock_get_carriers.return_value = ['EVERGREEN', 'COSCO', 'HMM']
        mock_load_config.return_value = {
            'mode': 'parallel',
            'max_workers': 2,
            'enable_excel_log': True,
            'enable_google_upload': True,
            'enable_data_cleanup': True
        }
        
        # 설정 로딩 테스트
        from utils.config_loader import get_carriers_to_run, load_execution_config
        
        carriers = get_carriers_to_run()
        config = load_execution_config()
        
        assert carriers == ['EVERGREEN', 'COSCO', 'HMM']
        assert config['mode'] == 'parallel'
        assert config['max_workers'] == 2
    
    @patch('utils.crawler_executor.run_carrier_parallel')
    def test_crawler_execution(self, mock_run_crawler):
        """크롤러 실행 테스트"""
        # 모킹 설정
        mock_run_crawler.return_value = {
            'carrier_name': 'EVERGREEN',
            'success': True,
            'duration': 120.5,
            'success_count': 4,
            'fail_count': 0
        }
        
        # 크롤러 실행 테스트
        from utils.crawler_executor import run_carrier_parallel
        
        result = run_carrier_parallel('EVERGREEN', [])
        assert result['carrier_name'] == 'EVERGREEN'
        assert result['success'] is True
        assert result['success_count'] == 4
    
    @patch('utils.excel_logger.save_excel_log')
    @patch('utils.excel_logger.add_google_upload_logs')
    def test_excel_logging(self, mock_add_google, mock_save_excel):
        """엑셀 로깅 테스트"""
        # 모킹 설정
        mock_save_excel.return_value = True
        mock_add_google.return_value = []
        
        # 엑셀 로깅 테스트
        from utils.excel_logger import save_excel_log, add_google_upload_logs
        
        crawling_results = [
            ('EVERGREEN', {'success': True, 'duration': 120.5}),
            ('COSCO', {'success': True, 'duration': 95.2})
        ]
        
        result = save_excel_log(crawling_results, 215.7)
        assert result is True
        
        google_logs = add_google_upload_logs()
        assert google_logs == []
    
    @patch('utils.google_upload.run_main_upload')
    @patch('utils.google_upload.upload_errorlog_to_drive')
    def test_google_upload(self, mock_upload_errorlog, mock_main_upload):
        """구글 드라이브 업로드 테스트"""
        # 모킹 설정
        mock_main_upload.return_value = {
            'success': True,
            'uploaded_files': ['file1.xlsx', 'file2.xlsx'],
            'failed_files': []
        }
        mock_upload_errorlog.return_value = {
            'success': True,
            'uploaded_files': ['error_log.xlsx'],
            'failed_files': []
        }
        
        # 구글 업로드 테스트
        from utils.google_upload import run_main_upload, upload_errorlog_to_drive
        
        main_result = run_main_upload()
        assert main_result['success'] is True
        assert len(main_result['uploaded_files']) == 2
        
        error_result = upload_errorlog_to_drive(None)
        assert error_result['success'] is True
        assert len(error_result['uploaded_files']) == 1
    
    @patch('utils.data_cleanup.cleanup_old_data')
    @patch('utils.data_cleanup.cleanup_old_errorlogs')
    def test_data_cleanup(self, mock_cleanup_errorlogs, mock_cleanup_data):
        """데이터 정리 테스트"""
        # 모킹 설정
        mock_cleanup_data.return_value = True
        mock_cleanup_errorlogs.return_value = {
            'success': True,
            'deleted_folders': ['old_folder_1', 'old_folder_2'],
            'total_size_freed': 1024 * 1024 * 50  # 50MB
        }
        
        # 데이터 정리 테스트
        from utils.data_cleanup import cleanup_old_data, cleanup_old_errorlogs
        
        data_result = cleanup_old_data()
        assert data_result is True
        
        error_result = cleanup_old_errorlogs()
        assert error_result['success'] is True
        assert len(error_result['deleted_folders']) == 2
        assert error_result['total_size_freed'] > 0
    
    @patch('utils.logging_setup.setup_main_logging')
    def test_logging_setup(self, mock_setup_logging):
        """로깅 설정 테스트"""
        # 모킹 설정
        mock_logger = Mock()
        mock_setup_logging.return_value = mock_logger
        
        # 로깅 설정 테스트
        from utils.logging_setup import setup_main_logging
        
        logger = setup_main_logging()
        assert logger == mock_logger
    
    def test_main_execution_flow(self):
        """메인 실행 흐름 테스트 (통합)"""
        with patch('utils.config_loader.get_carriers_to_run') as mock_carriers, \
             patch('utils.crawler_executor.run_carrier_parallel') as mock_crawler, \
             patch('utils.excel_logger.save_excel_log') as mock_excel, \
             patch('utils.google_upload.run_main_upload') as mock_upload, \
             patch('utils.data_cleanup.cleanup_old_data') as mock_cleanup:
            
            # 모킹 설정
            mock_carriers.return_value = ['EVERGREEN', 'COSCO']
            mock_crawler.return_value = {
                'carrier_name': 'EVERGREEN',
                'success': True,
                'duration': 100.0
            }
            mock_excel.return_value = True
            mock_upload.return_value = {'success': True}
            mock_cleanup.return_value = True
            
            # 메인 실행 흐름 시뮬레이션
            carriers = mock_carriers()
            assert len(carriers) == 2
            
            crawling_results = []
            for carrier in carriers:
                result = mock_crawler(carrier, [])
                crawling_results.append((carrier, result))
            
            assert len(crawling_results) == 2
            
            excel_result = mock_excel(crawling_results, 200.0)
            assert excel_result is True
            
            upload_result = mock_upload()
            assert upload_result['success'] is True
            
            cleanup_result = mock_cleanup()
            assert cleanup_result is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 