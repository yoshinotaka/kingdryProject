import os
import paramiko
from datetime import datetime
import logging
import fnmatch
from config.download_config import DOWNLOAD_CONFIG, db
from models import Item

class FileDownloader:
    def __init__(self):
        self.config = DOWNLOAD_CONFIG
        self.setup_logging()
        self.setup_database()

    def setup_logging(self):
        """ロギングの設定"""
        log_path = self.config['download']['log_path']
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_database(self):
        """データベース接続の設定"""
        from flask import Flask
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://shipping_user:shipping_password@kingproject-db/shipping_db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def is_regular_file(self, sftp, path):
        """指定されたパスが通常のファイルかどうかを判定"""
        try:
            file_stat = sftp.stat(path)
            return not file_stat.st_mode & 0o40000  # ディレクトリの場合はFalseを返す
        except IOError:
            return False

    def get_today_date(self):
        """今日の日付をYYYY-MM-DD形式で取得"""
        return datetime.now().strftime('%Y-%m-%d')

    def download_files(self):
        """指定されたファイルをダウンロード"""
        try:
            # ローカル保存先ディレクトリの作成
            local_path = self.config['download']['local_path']
            self.logger.info(f"ローカル保存先ディレクトリ: {local_path}")
            os.makedirs(local_path, exist_ok=True)
            self.logger.info(f"ディレクトリ作成完了: {os.path.exists(local_path)}")

            # SSHクライアントの設定
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # リモートサーバーに接続
            self.logger.info(f"リモートサーバーに接続中: {self.config['remote_server']['host']}")
            ssh.connect(
                hostname=self.config['remote_server']['host'],
                username=self.config['remote_server']['username'],
                password=self.config['remote_server']['password'],
                port=self.config['remote_server']['port']
            )
            self.logger.info("リモートサーバー接続成功")
            
            # SCPクライアントの作成
            scp = ssh.open_sftp()
            self.logger.info("SFTPセッション確立")
            
            # リモートディレクトリ内のファイルを取得
            remote_path = self.config['download']['remote_path']
            today = self.get_today_date()
            file_pattern = f"uriage_daityo_oazukaribi_shitei{today}-*.csv"
            
            self.logger.info(f"リモートパス: {remote_path}")
            self.logger.info(f"ファイルパターン: {file_pattern}")
            
            # リモートディレクトリ内のファイル一覧を取得
            files = scp.listdir(remote_path)
            self.logger.info(f"リモートディレクトリ内のファイル数: {len(files)}")
            
            # パターンマッチしたファイルをカウント
            matched_files = []
            for filename in files:
                if fnmatch.fnmatch(filename, file_pattern):
                    remote_file = os.path.join(remote_path, filename)
                    if self.is_regular_file(scp, remote_file):
                        matched_files.append(filename)
                    else:
                        self.logger.warning(f"ディレクトリまたは特殊ファイルはスキップします: {filename}")
            
            self.logger.info(f"パターンマッチしたファイル数: {len(matched_files)}")
            
            # ダウンロードしたファイル数をカウント
            downloaded_count = 0
            
            # ファイルのダウンロード
            for filename in matched_files:
                remote_file = os.path.join(remote_path, filename)
                local_file = os.path.join(local_path, filename)
                
                self.logger.info(f"ダウンロード開始: {filename}")
                self.logger.info(f"リモートファイル: {remote_file}")
                self.logger.info(f"ローカルファイル: {local_file}")
                
                scp.get(remote_file, local_file)
                downloaded_count += 1
                self.logger.info(f"ダウンロード完了: {filename}")
            
            # ダウンロード結果のサマリーを出力
            self.logger.info(f"ダウンロード完了: {downloaded_count}/{len(matched_files)} ファイルをダウンロードしました")
            
            # 接続を閉じる
            scp.close()
            ssh.close()
            self.logger.info("すべてのファイルのダウンロードが完了しました")
            
        except Exception as e:
            self.logger.error(f"エラーが発生しました: {str(e)}")
            raise

if __name__ == "__main__":
    downloader = FileDownloader()
    downloader.download_files() 