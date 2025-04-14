from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Item
from forms import ShippingForm
from datetime import datetime
import os
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://shipping_user:shipping_password@db/shipping_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# アプリケーションコンテキスト内でテーブルを作成
def init_db():
    try:
        with app.app_context():
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

# アプリケーション起動時にテーブルを作成
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shipping_list')
def shipping_list():
    # 出荷状況の一覧を取得
    items = Item.query.order_by(Item.created_at.desc()).all()
    return render_template('shipping_list.html', items=items)

@app.route('/shipping', methods=['GET', 'POST'])
def shipping():
    form = ShippingForm()
    if form.validate_on_submit():
        # 指定された店舗IDとタグ1に一致する商品を検索
        items = Item.query.filter_by(
            shop_id=form.shop_id.data,
            tag1=form.tag1.data
        ).all()
        
        if not items:
            flash('該当する商品が見つかりませんでした。', 'error')
            return redirect(url_for('shipping'))
        
        # 出荷情報を更新
        for item in items:
            if form.factory_staff_id.data:
                item.factory_staff_id = form.factory_staff_id.data
            if form.factory_staff_name.data:
                item.factory_staff_name = form.factory_staff_name.data
            if form.factory_location.data:
                item.factory_location = form.factory_location.data
            if form.syukka_date.data:
                item.syukka_date = form.syukka_date.data
            if form.syukka_time.data:
                item.syukka_time = form.syukka_time.data
            if form.packaging_shape.data:
                item.packaging_shape = form.packaging_shape.data
            if form.factory_comment.data:
                item.factory_comment = form.factory_comment.data
            item.syukka_flag = 1
            item.factory_process_datetime = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('出荷情報が正常に更新されました。', 'success')
            return redirect(url_for('shipping'))
        except Exception as e:
            db.session.rollback()
            flash(f'エラーが発生しました: {str(e)}', 'error')
    
    return render_template('shipping.html', form=form)

@app.route('/reship', methods=['GET', 'POST'])
def reship():
    form = ShippingForm()
    if form.validate_on_submit():
        items = Item.query.filter_by(
            shop_id=form.shop_id.data,
            tag1=form.tag1.data
        ).all()
        
        if not items:
            flash('該当する商品が見つかりませんでした。', 'error')
            return redirect(url_for('reship'))
        
        for item in items:
            item.factory_staff_id = form.factory_staff_id.data
            item.factory_staff_name = form.factory_staff_name.data
            item.factory_location = form.factory_location.data
            item.syukka_date = form.syukka_date.data
            item.syukka_time = form.syukka_time.data
            item.packaging_shape = form.packaging_shape.data
            item.factory_comment = form.factory_comment.data
            item.syukka_flag = 1
            item.factory_process_datetime = datetime.utcnow()
            item.status = 'reship'
        
        try:
            db.session.commit()
            flash('再出荷情報が正常に更新されました。', 'success')
            return redirect(url_for('reship'))
        except Exception as e:
            db.session.rollback()
            flash(f'エラーが発生しました: {str(e)}', 'error')
    
    return render_template('reship.html', form=form)

@app.route('/return', methods=['GET', 'POST'])
def return_item():
    form = ShippingForm()
    if form.validate_on_submit():
        items = Item.query.filter_by(
            shop_id=form.shop_id.data,
            tag1=form.tag1.data
        ).all()
        
        if not items:
            flash('該当する商品が見つかりませんでした。', 'error')
            return redirect(url_for('return_item'))
        
        for item in items:
            item.factory_staff_id = form.factory_staff_id.data
            item.factory_staff_name = form.factory_staff_name.data
            item.factory_location = form.factory_location.data
            item.return_datetime = datetime.utcnow()
            item.factory_comment = form.factory_comment.data
            item.status = 'returned'
        
        try:
            db.session.commit()
            flash('返却情報が正常に更新されました。', 'success')
            return redirect(url_for('return_item'))
        except Exception as e:
            db.session.rollback()
            flash(f'エラーが発生しました: {str(e)}', 'error')
    
    return render_template('return.html', form=form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 