import pandas as pd
import re
import csv
import os
import fnmatch
from datetime import datetime
from config.download_config import DOWNLOAD_CONFIG, db
from models import Item

def get_today_date():
    """今日の日付をYYYY-MM-DD形式で取得"""
    return datetime.now().strftime('%Y-%m-%d')

def parse_date(date_str):
    """日付文字列をパースしてdatetimeオブジェクトに変換"""
    if not date_str or date_str == '-':
        return None
    try:
        return datetime.strptime(date_str, '%Y/%m/%d')
    except ValueError:
        return None

def process_csv_files(directory_path, file_pattern=None):
    """指定ディレクトリ内のパターンに一致するCSVファイルを処理"""
    processed_count = 0
    
    try:
        # ディレクトリが存在するか確認
        if not os.path.exists(directory_path):
            print(f"ディレクトリが見つかりません: {directory_path}")
            return
        
        # ファイルパターンが指定されていない場合は今日の日付を使用
        if file_pattern is None:
            today = get_today_date()
            file_pattern = f"uriage_daityo_oazukaribi_shitei{today}-*.csv"
        
        # ディレクトリ内のファイルを取得
        files = os.listdir(directory_path)
        matching_files = [f for f in files if fnmatch.fnmatch(f, file_pattern)]
        
        print(f"一致するファイル数: {len(matching_files)}")
        
        # 各ファイルを処理
        for filename in matching_files:
            file_path = os.path.join(directory_path, filename)
            print(f"処理中: {filename}")
            
            records_imported = process_single_csv(file_path)
            processed_count += records_imported
            
        print(f"処理完了。合計 {processed_count} 件のレコードをインポートしました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def process_single_csv(csv_file_path):
    """単一のCSVファイルを pandas で処理して SQLAlchemy 経由でデータベースに挿入"""
    records_count = 0

    try:
        # pandasでCSVを読み込む（先頭7行スキップ）
        df = pd.read_csv(csv_file_path, encoding='utf-8', skiprows=7)

        # 不要な "Unnamed" カラムを除去
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # データ挿入リスト作成
        for index, row in df.iterrows():
            try:
                # 店舗コードの抽出（0002:オザム日の出店 → 002）
                tenpo_original = str(row.get("店舗", ""))
                tenpo_code = ""
                match = re.search(r'^0*(\d{3})[:：]', tenpo_original)
                if match:
                    tenpo_code = match.group(1)
                elif tenpo_original.isdigit():
                    tenpo_code = tenpo_original

                # タグ処理（01-234 → 1234）
                tag_raw = str(row.get("タグ", "")).strip()
                numeric_tag = None  # デフォルト値をNoneに設定
                
                if tag_raw and tag_raw.lower() != 'nan' and tag_raw != '-':
                    if '-' in tag_raw:
                        parts = tag_raw.split('-')
                        prefix = parts[0].lstrip('0') or '0'
                        numeric_tag = prefix + parts[1]
                    else:
                        numeric_tag = tag_raw.replace('-', '')

                # 数値変換
                def parse_float(value):
                    try:
                        return float(str(value).replace(',', ''))
                    except (ValueError, TypeError):
                        return 0.0

                # 日付変換
                def parse_date(value):
                    try:
                        return datetime.strptime(value.strip(), "%Y/%m/%d") if pd.notna(value) else None
                    except:
                        return None

                item = Item(
                    shop_id=int(tenpo_code) if tenpo_code.isdigit() else 0,
                    denpyo_no=str(row.get("伝票No", "")).strip(),
                    tag1=numeric_tag,  # Noneの場合はNULLとして保存
                    shohin_code=str(row.get("商品ｺｰﾄﾞ", "")).strip() or "0000",
                    shohin_name=str(row.get("商品名", "")).strip() or "不明",
                    kokyaku_code=str(row.get("顧客ｺｰﾄﾞ", "")).strip(),
                    kokyaku_name=str(row.get("顧客名", "")).strip(),
                    cost_price=parse_float(row.get("単価", 0)),
                    selling_price=parse_float(row.get("売価", 0)),
                    nyuuka_code=str(row.get("入荷", "")).strip(),
                    syukka_code=str(row.get("出荷", "")).strip(),
                    azukari_date=parse_date(row.get("預り日")),
                    shiage_date=parse_date(row.get("仕上日")),
                    return_datetime=parse_date(row.get("返却日時")),
                    image_path=str(row.get("画像", "")).strip(),
                    signature_path=str(row.get("サイン", "")).strip(),
                    tag2=str(row.get("タグ2", "")).strip(),
                    status="取消" if str(row.get("取消", "")).strip() == "取" else "通常"
                )

                db.session.add(item)
                records_count += 1

            except Exception as row_error:
                print(f"[行 {index + 1}] データ処理エラー: {row_error}")
                continue

        db.session.commit()
        print(f"ファイル '{os.path.basename(csv_file_path)}' から {records_count} 件のレコードをインポートしました")

    except Exception as e:
        db.session.rollback()
        print(f"ファイル処理中にエラーが発生しました: {e}")

    return records_count

# 実行例
if __name__ == "__main__":
    # アプリケーションコンテキスト内で実行する必要があります
    from app import app
    with app.app_context():
        directory_path = "batch/download"  # パスを修正
        file_pattern = "uriage_daityo_oazukaribi_shitei2025-04-*.csv"  # パターンを修正
       
        process_csv_files(directory_path, file_pattern)



        