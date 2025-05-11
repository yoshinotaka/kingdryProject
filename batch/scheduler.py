# スケジューリング用のライブラリ
import schedule  # 定期実行のスケジューリング
import time  # 時間待機と時刻取得

# 日付処理用のライブラリ
from datetime import datetime  # 日付と時刻の操作

# アプリケーション固有のモジュール
from download_files import FileDownloader  # ファイルダウンロード機能
from insert_files import process_csv_files  # CSVファイル処理機能

# ロギングとファイルシステム操作
import logging  # ログ記録
import os  # ファイルシステム操作

def setup_logging():
    """ロギングの設定"""
    log_dir = "batch/logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "scheduler.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def get_today_date():
    """今日の日付をYYYY-MM-DD形式で取得"""
    return datetime.now().strftime('%Y-%m-%d')

def download_and_process():
    """ファイルのダウンロードと処理を実行"""
    logger = setup_logging()
    today = get_today_date()
    
    try:
        # ファイルのダウンロード
        logger.info(f"ダウンロード処理開始: {today}")
        downloader = FileDownloader()
        downloader.download_files()
        
        # ファイルの処理
        logger.info(f"データベース挿入処理開始: {today}")
        directory_path = "batch/download"
        file_pattern = f"uriage_daityo_oazukaribi_shitei{today}-*.csv"
        
        process_csv_files(directory_path, file_pattern)
        
        logger.info(f"処理完了: {today}")
        
    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    download_and_process() 