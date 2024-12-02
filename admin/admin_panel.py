from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore
import logging
import os

logging.basicConfig(level=logging.DEBUG)

# تهيئة تطبيق Flask
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_default_secret_key')  # استخدم المتغيرات البيئية من أجل الأمان

# تهيئة Firebase Admin SDK
cred = credentials.Certificate("amrobisk-serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# تهيئة قاعدة بيانات Firestore
db = firestore.client()

# بيانات الاعتماد الثابتة (يفضل تخزينها بشكل آمن)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# صفحة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_home'))
        else:
            return render_template('login.html', error="البيانات غير صحيحة!")

    return render_template('login.html')

# صفحة الخروج (تسجيل الخروج)
@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # حذف حالة تسجيل الدخول
    return redirect(url_for('login'))

# صفحة الرئيسية للمدير
@app.route('/admin')
def admin_home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

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
            'image_url': product_data.get('image_url')
        })

    return render_template('admin_home.html', products=product_list)

# صفحة إضافة منتج جديد
@app.route('/admin/add', methods=['GET', 'POST'])
def add_product():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']

        # التحقق من صحة البيانات
        if not name or not price or not description:
            return render_template('add_product.html', error="جميع الحقول مطلوبة.")
        
        try:
            price = float(price)
        except ValueError:
            return render_template('add_product.html', error="السعر غير صحيح.")

        # إضافة المنتج إلى Firestore
        db.collection('products').add({
            'name': name,
            'description': description,
            'price': price,
            'image_url': image_url
        })
        return redirect(url_for('admin_home'))

    return render_template('add_product.html')

# صفحة تعديل منتج
@app.route('/admin/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    product_ref = db.collection('products').document(product_id)
    product = product_ref.get()

    if not product.exists:
        return "المنتج غير موجود", 404

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']

        try:
            price = float(price)
        except ValueError:
            return render_template('edit_product.html', error="السعر غير صحيح.", product=product.to_dict())

        # تحديث المنتج في Firestore
        product_ref.update({
            'name': name,
            'description': description,
            'price': price,
            'image_url': image_url
        })
        return redirect(url_for('admin_home'))

    product_data = product.to_dict()
    return render_template('edit_product.html', product=product_data, product_id=product_id)

# صفحة حذف منتج
@app.route('/admin/delete/<product_id>')
def delete_product(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    product_ref = db.collection('products').document(product_id)
    product_ref.delete()
    return redirect(url_for('admin_home'))

if __name__ == '__main__':
    app.run(debug=True)
