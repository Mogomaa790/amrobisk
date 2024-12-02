from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore
import logging
logging.basicConfig(level=logging.DEBUG)



app = Flask(__name__)

# تهيئة Firebase Admin SDK
cred = credentials.Certificate("amrobisk-serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# تهيئة قاعدة بيانات Firestore
db = firestore.client()

# الصفحة الرئيسية
@app.route('/')
def home():
    products_ref = db.collection('products')
    products = products_ref.stream()
    product_list = []
    for product in products:
        product_data = product.to_dict()
        product_list.append({
            'id': product.id,
            'name': product_data.get('name'),
            'description': product_data.get('description'),
            'price': product_data.get('price'),
            'image_url': product_data.get('image_url')  # Add image_url field
        })
    return render_template('index.html', products=product_list)

# صفحة تفاصيل المنتج
@app.route('/product/<product_id>')
def product_detail(product_id):
    product_ref = db.collection('products').document(product_id)
    product = product_ref.get()

    if product.exists:
        product_data = product.to_dict()
        return render_template('product_detail.html', product=product_data)
    else:
        return "المنتج غير موجود", 404

if __name__ == '__main__':
    app.run(debug=True)
