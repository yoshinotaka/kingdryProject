from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 基本情報
    shop_id = db.Column(db.SmallInteger, nullable=False)
    denpyo_no = db.Column(db.String(20), nullable=False)
    tag1 = db.Column(db.String(20))
    shohin_code = db.Column(db.String(20), nullable=False)
    shohin_name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20))
    contents = db.Column(db.String(200))
    packaging_shape = db.Column(db.String(30))
    
    # 顧客情報
    kokyaku_code = db.Column(db.String(20))
    kokyaku_name = db.Column(db.String(50))
    
    # 金額情報
    cost_price = db.Column(db.Numeric(10, 2))
    selling_price = db.Column(db.Numeric(10, 2))
    tax_status = db.Column(db.String(10))
    
    # 入出荷情報
    nyuuka_code = db.Column(db.String(20))
    syukka_code = db.Column(db.String(20))
    course = db.Column(db.String(50))
    higiri_flag = db.Column(db.SmallInteger, default=0)
    delivery_date = db.Column(db.DateTime)
    syukka_date = db.Column(db.DateTime)
    syukka_time = db.Column(db.String(20))
    syukka_flag = db.Column(db.SmallInteger, default=0)
    seikyuu_flag = db.Column(db.SmallInteger, default=0)
    
    # 保管・処理情報
    azukari_date = db.Column(db.DateTime)
    shiage_date = db.Column(db.DateTime)
    return_datetime = db.Column(db.DateTime)
    
    # 工場情報
    factory_staff_id = db.Column(db.String(10))
    factory_staff_name = db.Column(db.String(30))
    factory_location = db.Column(db.String(50))
    factory_process_datetime = db.Column(db.DateTime)
    factory_comment = db.Column(db.Text)
    
    # タグ情報補足
    tag2 = db.Column(db.String(20))
    
    # その他
    status = db.Column(db.String(20))
    comment = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    signature_path = db.Column(db.String(255))
    
    # 監査情報
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Item {self.shohin_code}: {self.shohin_name}>' 