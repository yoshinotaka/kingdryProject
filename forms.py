from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Optional

class ShippingForm(FlaskForm):
    shop_id = StringField('店舗ID', validators=[DataRequired()])
    tag1 = StringField('タグ1', validators=[DataRequired()])
    factory_staff_id = StringField('工場担当者ID', validators=[Optional()])
    factory_staff_name = StringField('工場担当者名', validators=[Optional()])
    factory_location = StringField('工場場所', validators=[Optional()])
    syukka_date = DateTimeField('出荷日', format='%Y-%m-%d', validators=[Optional()])
    syukka_time = SelectField('出荷便', 
                             choices=[
                                 ('AM', 'AM便'),
                                 ('PM', 'PM便'),
                                 ('middle', '中間'),
                                 ('final', '最終')
                             ],
                             validators=[Optional()])
    packaging_shape = StringField('商品包装形状', validators=[Optional()])
    factory_comment = TextAreaField('工場コメント', validators=[Optional()]) 