from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from models import db, Item, ShippingLog
from forms import ShippingForm
from datetime import datetime, timedelta
import os
import logging
from flask_migrate import Migrate
from weasyprint import HTML
import tempfile

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://shipping_user:shipping_password@db/shipping_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

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

def find_items_by_shop_and_tag(shop_id, tag1):
    """
    店舗IDとタグ1に一致する商品を検索する共通関数
    """
    # 現在の日付から3か月前の日付を計算
    three_months_ago = datetime.utcnow().date() - timedelta(days=90)
    
    items = Item.query.filter_by(
        shop_id=shop_id,
        tag1=tag1
    ).filter(
        Item.azukari_date >= three_months_ago  # 3か月以内の制限を追加
    ).all()
    
    if not items:
        return None, f'店舗ID: {shop_id}, タグ番号: {tag1} の商品が見つかりませんでした。'
    
    # 複数件のチェックを削除し、全てのアイテムを返す
    return items, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shipping_list')
def shipping_list():
    # 初期表示用に50件のみ取得（お預かり日で降順）
    items = Item.query.order_by(Item.azukari_date.desc()).limit(50).all()
    today = datetime.utcnow().date().strftime('%Y-%m-%d')
    return render_template('shipping_list.html', items=items, today=today)

@app.route('/api/shipping_list')
def api_shipping_list():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # 絞り込みパラメータを取得
    shop_id = request.args.get('shop_id')
    denpyo_no = request.args.get('denpyo_no')
    tag1 = request.args.get('tag1')
    status = request.args.get('status')
    
    per_page = 50
    offset = (page - 1) * per_page
    
    # クエリの基本設定
    query = Item.query.filter(Item.tag1.isnot(None))  # tag1がNULLでないレコードのみを取得
    
    # 絞り込み条件を追加（完全一致）
    if shop_id:
        query = query.filter(Item.shop_id == shop_id)
    if denpyo_no:
        query = query.filter(Item.denpyo_no == denpyo_no)
    if tag1:
        query = query.filter(Item.tag1 == tag1)
    if status:
        if status == 'shipped':
            query = query.filter(Item.syukka_flag == 1)
        elif status == 'unshipped':
            query = query.filter(Item.syukka_flag == 0)
        elif status == 'reship':
            query = query.filter(Item.status == 'reship')
        elif status == 'returned':
            query = query.filter(Item.status == 'returned')
    
    # ソート対象のカラムを取得
    column = getattr(Item, sort_by, None)
    if column is None:
        column = Item.created_at
    
    # ソート順を設定
    if sort_order == 'asc':
        order_by = column.asc()
    else:
        order_by = column.desc()
    
    # ソートを適用
    query = query.order_by(order_by)
    
    # ページネーションを適用
    items = query.offset(offset).limit(per_page).all()
    
    return jsonify({
        'items': [{
            'shop_id': item.shop_id,
            'azukari_date': item.azukari_date.strftime('%Y-%m-%d') if item.azukari_date else None,
            'tag1': item.tag1,
            'course': item.course,
            'color': item.color,
            'contents': item.contents,
            'packaging_shape': item.packaging_shape,
            'syukka_date': item.syukka_date.strftime('%Y-%m-%d') if item.syukka_date else None,
            'syukka_time': item.syukka_time,
            'factory_staff_name': item.factory_staff_name,
            'status': item.status,
            'syukka_flag': item.syukka_flag,
            'shohin_name': item.shohin_name
        } for item in items]
    })

@app.route('/api/process_shipping', methods=['POST'])
def process_shipping():
    try:
        data = request.get_json()
        shop_id = data.get('shop_id')
        tag1 = data.get('tag1')
        syukka_date = data.get('syukka_date')
        syukka_time = data.get('syukka_time')
        factory_staff_name = data.get('factory_staff_name')
        packaging_shape = data.get('packaging_shape')
        
        if not shop_id or not tag1:
            return jsonify({'error': '店舗IDとタグ1は必須です'}), 400
        
        items, error = find_items_by_shop_and_tag(shop_id, tag1)
        if error:
            return jsonify({'error': error}), 404
        
        # 全ての該当商品の出荷情報を更新
        update_count = 0
        updated_items = []
        for item in items:
            item.syukka_flag = 1
            item.syukka_date = datetime.strptime(syukka_date, '%Y-%m-%d').date() if syukka_date else datetime.utcnow().date()
            item.syukka_time = syukka_time
            item.factory_staff_name = factory_staff_name
            item.packaging_shape = packaging_shape
            item.factory_process_datetime = datetime.utcnow()
            update_count += 1
            updated_items.append({
                'shop_id': item.shop_id,
                'tag1': item.tag1,
                'azukari_date': item.azukari_date.strftime('%Y-%m-%d') if item.azukari_date else None,
                'packaging_shape': item.packaging_shape,
                'syukka_date': item.syukka_date.strftime('%Y-%m-%d') if item.syukka_date else None,
                'syukka_time': item.syukka_time,
                'factory_staff_name': item.factory_staff_name
            })
            
            # ログを保存
            log = ShippingLog(
                shop_id=item.shop_id,
                tag1=item.tag1,
                azukari_date=item.azukari_date,
                update_count=update_count
            )
            db.session.add(log)
        
        db.session.commit()
        
        # デバッグ用ログ
        logger.info(f"出荷処理完了: {update_count}件更新")
        logger.info(f"更新した商品: {updated_items}")
        
        response = {
            'message': f'出荷処理が完了しました（{update_count}件更新）',
            'updated_items': updated_items
        }
        logger.info(f"レスポンス: {response}")
        
        return jsonify(response)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"出荷処理中にエラーが発生しました: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/shipping', methods=['GET', 'POST'])
def shipping():
    form = ShippingForm()
    if form.validate_on_submit():
        items, error = find_items_by_shop_and_tag(form.shop_id.data, form.tag1.data)
        if error:
            flash(error, 'error')
            return redirect(url_for('shipping'))
        
        update_count = 0
        for item in items:
            # 出荷情報を更新
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
            update_count += 1
        
        try:
            db.session.commit()
            flash(f'出荷情報が正常に更新されました。（{update_count}件更新）', 'success')
            return redirect(url_for('shipping'))
        except Exception as e:
            db.session.rollback()
            flash(f'エラーが発生しました: {str(e)}', 'error')
    
    return render_template('shipping.html', form=form)

@app.route('/reship', methods=['GET', 'POST'])
def reship():
    form = ShippingForm()
    if form.validate_on_submit():
        item, error = find_items_by_shop_and_tag(form.shop_id.data, form.tag1.data)
        if error:
            flash(error, 'error')
            return redirect(url_for('reship'))
        
        # 再出荷情報を更新
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
        item, error = find_items_by_shop_and_tag(form.shop_id.data, form.tag1.data)
        if error:
            flash(error, 'error')
            return redirect(url_for('return_item'))
        
        # 返却情報を更新
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

@app.route('/shipping_detail/<int:shop_id>/<tag1>')
def shipping_detail(shop_id, tag1):
    item = Item.query.filter_by(shop_id=shop_id, tag1=tag1).first()
    if not item:
        return jsonify({'error': '該当する商品が見つかりませんでした。'}), 404
    return render_template('shipping_detail.html', item=item)

@app.route('/logs')
def show_logs():
    logs = ShippingLog.query.order_by(ShippingLog.timestamp.desc()).all()
    return render_template('logs.html', logs=logs)

@app.route('/api/logs')
def get_logs():
    shop_id = request.args.get('shop_id')
    tag1 = request.args.get('tag1')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = ShippingLog.query
    
    if shop_id:
        query = query.filter(ShippingLog.shop_id == shop_id)
    if tag1:
        query = query.filter(ShippingLog.tag1 == tag1)
    if date_from:
        query = query.filter(ShippingLog.timestamp >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(ShippingLog.timestamp <= datetime.strptime(date_to, '%Y-%m-%d'))
    
    logs = query.order_by(ShippingLog.timestamp.desc()).all()
    
    return jsonify({
        'logs': [{
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'shop_id': log.shop_id,
            'tag1': log.tag1,
            'azukari_date': log.azukari_date.strftime('%Y-%m-%d') if log.azukari_date else None,
            'update_count': log.update_count
        } for log in logs]
    })

@app.route('/shop_list')
def shop_list():
    # ユニークな店舗IDのリストを取得
    shop_ids = db.session.query(Item.shop_id).distinct().order_by(Item.shop_id).all()
    shop_ids = [shop_id[0] for shop_id in shop_ids]
    return render_template('shop_list.html', shop_ids=shop_ids)

@app.route('/shop_items')
def shop_items():
    shop_id = request.args.get('shop_id')
    if not shop_id:
        flash('店舗を選択してください。', 'error')
        return redirect(url_for('shop_list'))
    
    # 初期表示用に50件のみ取得
    items = Item.query.filter_by(shop_id=shop_id)\
        .order_by(Item.azukari_date.desc())\
        .limit(50)\
        .all()
    return render_template('shop_items.html', items=items, shop_id=shop_id)

@app.route('/api/shop_items')
def api_shop_items():
    shop_id = request.args.get('shop_id')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page
    
    if not shop_id:
        return jsonify({'error': '店舗IDは必須です'}), 400
    
    # 店舗IDで絞り込んだ商品一覧を取得
    items = Item.query.filter_by(shop_id=shop_id)\
        .order_by(Item.azukari_date.desc())\
        .offset(offset)\
        .limit(per_page)\
        .all()
    
    return jsonify({
        'items': [{
            'azukari_date': item.azukari_date.strftime('%Y-%m-%d') if item.azukari_date else '',
            'tag1': item.tag1,
            'course': item.course,
            'color': item.color,
            'contents': item.contents,
            'packaging_shape': item.packaging_shape,
            'syukka_date': item.syukka_date.strftime('%Y-%m-%d') if item.syukka_date else '',
            'syukka_time': item.syukka_time,
            'factory_staff_name': item.factory_staff_name,
            'status': item.status,
            'shohin_name': item.shohin_name
        } for item in items]
    })

@app.route('/shipping_list/pdf')
def shipping_list_pdf():
    return render_template('shipping_list_pdf.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 