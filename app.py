# app.py
from flask import Flask, render_template, jsonify, session, redirect, url_for, request, current_app
import json
import os
import datetime
from systemBot import *
from functools import wraps
from PIL import Image
import uuid

app = Flask(__name__)

# Настройки PayPallych
PALLY_MERCHANT_ID = "ваш_merchant_id"  # ← получите в личном кабинете pally.info

app.secret_key = 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'  # ← замените на сложную строку!

# Учётные данные админа (в продакшене — храните в .env или БД)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '123456'  # ← ОБЯЗАТЕЛЬНО измените!

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def load_catalog():
    with open(os.path.join(app.root_path, 'data', 'catalog.json'), 'r', encoding='utf-8') as f:
        return json.load(f)
    
def load_portfolio():
    with open(os.path.join(app.root_path, 'data', 'portfolio.json'), 'r', encoding='utf-8') as f:
        return json.load(f)
    
def load_articles():
    with open(os.path.join(app.root_path, 'data', 'articles.json'), 'r', encoding='utf-8') as f:
        return json.load(f)
    
def load_messages():
    filepath = os.path.join(app.root_path, 'data', 'messages.json')
    
    # Если файл не существует — возвращаем пустой список
    if not os.path.exists(filepath):
        return []
    
    # Если файл существует, но пустой — тоже возвращаем пустой список
    if os.path.getsize(filepath) == 0:
        return []
    
    # Иначе читаем как JSON
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # На случай, если файл повреждён — возвращаем пустой список
            return []

def save_messages(messages):
    filepath = os.path.join(app.root_path, 'data', 'messages.json')
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)
    
def get_item_by_id(item_id):
    try:
        item_id = int(item_id)
        items = load_catalog()
        for item in items:
            if item.get('id') == item_id:
                return item
    except (ValueError, TypeError):
        pass
    return None

def save_order(data):
    filepath = os.path.join(app.root_path, 'data', 'orders.json')
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    order_id = str(uuid.uuid4())[:8]
    order = {
        "order_id": order_id,
        "timestamp": datetime.now().isoformat(),
        "status": "pending",
        "item_id": data["item_id"],
        "item_name": data["item_name"],
        "amount": data["amount"],
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"]
    }
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            orders = json.load(f)
    else:
        orders = []
    
    orders.append(order)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)
    
    return order_id

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image_as_webp(image_file):
    """Принимает FileStorage, возвращает имя сохранённого .webp файла"""
    if not image_file or not allowed_file(image_file.filename):
        return None

    # Генерируем уникальное имя
    filename = f"work_{uuid.uuid4().hex}.webp"
    filepath = os.path.join(app.root_path, 'static', 'media', filename)

    # Открываем изображение и конвертируем в WebP
    img = Image.open(image_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")  # WebP без прозрачности (меньше размер)
    img.save(filepath, 'WEBP', quality=85)

    return filename

@app.route('/order')
def order_form():
    item_id = request.args.get('item_id')
    item = get_item_by_id(item_id)
    if not item:
        return "Товар не найден", 404
    return render_template('order.html', item=item, item_id=item['id'])

@app.route('/')
def index():
    # Загружаем каталог, чтобы получить категории
    catalog_items = load_catalog()
    categories = sorted({item['category'] for item in catalog_items if item.get('category')})
    
    directions = [
        {"title": "Прототипирование", "description": "Быстрое создание моделей для тестирования", "image": "/static/media/proto.jpg"},
        {"title": "Архитектура", "description": "Макеты зданий и сооружений", "image": "/static/media/arch.jpg"},
        {"title": "Медицина", "description": "Анатомические модели и протезы", "image": "/static/media/med.jpg"},
    ]
    return render_template('index.html', directions=directions, categories=categories)

#фильтр по времени
@app.template_filter('strftime')
def _jinja2_filter_datetime(date_str, fmt='%d %B %Y'):
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        # Для русских названий месяцев (опционально)
        import locale
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        return date.strftime(fmt)
    except:
        return date_str

# Словарь месяцев на русском
MONTHS = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря'
}

@app.template_filter('format_date')
def _jinja2_filter_date(date_str):
    try:
        d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return f"{d.day} {MONTHS[d.month]} {d.year}"
    except (ValueError, KeyError, TypeError):
        return date_str

@app.route('/catalog')
def catalog():
    all_items = load_catalog()
    
    # Получаем уникальные категории для фильтра
    categories = sorted({item['category'] for item in all_items if item.get('category')})
    
    # Применяем фильтрацию
    category_filter = request.args.get('category')
    query = request.args.get('q')

    items = all_items
    if category_filter:
        items = [item for item in items if item.get('category') == category_filter]
    if query:
        items = [item for item in items if query.lower() in item['name'].lower() or query.lower() in item.get('description', '').lower()]

    return render_template('catalog.html', items=items, categories=categories, active_category=category_filter)

@app.route('/search')
def search():
    return catalog()  # переиспользуем логику каталога

# Остальные страницы — простые шаблоны
@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/materials')
def materials():
    materials_data = [
        {
            "name": "PLA",
            "type": "Биопластик",
            "description": "Экологичный, легко печатается, подходит для декора и прототипов.",
            "properties": ["Без запаха", "Жёсткий", "Не термостойкий"]
        },
        {
            "name": "ABS",
            "type": "Инженерный пластик",
            "description": "Прочный, термостойкий, но требует закрытой камеры.",
            "properties": ["Ударопрочный", "Термостойкий", "С запахом"]
        },
        {
            "name": "PETG",
            "type": "Универсальный",
            "description": "Сочетает прочность ABS и простоту PLA. Водонепроницаем.",
            "properties": ["Прочный", "Гибкий", "Химически стойкий"]
        }
    ]
    return render_template('materials.html', materials=materials_data)

@app.route('/delivery')
def delivery():
    return render_template('delivery.html')

# Список всех статей
@app.route('/articles')
def articles():
    article_list = load_articles()
    return render_template('articles.html', articles=article_list)

# Отдельная статья
@app.route('/articles/<slug>')
def article_detail(slug):
    article_list = load_articles()
    article = next((a for a in article_list if a['slug'] == slug), None)
    if not article:
        return render_template('404.html'), 404
    return render_template('article_detail.html', article=article)

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

# API для обратного звонка (можно расширить)
@app.route('/api/callback', methods=['POST'])
def callback():
    data = request.get_json()
    # Здесь можно сохранить в БД или отправить email
    print("Запрос на звонок:", data)
    return jsonify({"status": "success"})

@app.route('/catalog/<int:item_id>')
def catalog_item(item_id):
    items = load_catalog()
    item = next((item for item in items if item.get('id') == item_id), None)
    if item is None:
        return render_template('404.html'), 404  # или просто abort(404)
    return render_template('catalog_item.html', item=item)

@app.route('/portfolio')
def portfolio():
    projects = load_portfolio()
    return render_template('portfolio.html', projects=projects)

@app.route('/payment/success')
def payment_success():
    order_id = request.args.get('order_id')
    if not order_id:
        return render_template('payment_fail.html', reason="Нет ID заказа")

    # Обновляем статус заказа на "paid"
    filepath = os.path.join(app.root_path, 'data', 'orders.json')
    if os.path.exists(filepath):
        with open(filepath, 'r+', encoding='utf-8') as f:
            orders = json.load(f)
            for order in orders:
                if order.get('order_id') == order_id:
                    order['status'] = 'paid'
                    order['paid_at'] = datetime.now().isoformat()
                    break
            f.seek(0)
            json.dump(orders, f, ensure_ascii=False, indent=2)
            f.truncate()

        # Отправляем уведомление в Telegram
        order_data = next((o for o in orders if o.get('order_id') == order_id), {})
        send_telegram_order_notification(order_data)

    return render_template('payment_success.html')

@app.route('/payment/fail')
def payment_fail():
    return render_template('payment_fail.html')

@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        item = get_item_by_id(item_id)
        
        if not item:
            return jsonify({"error": "Товар не найден"}), 400
        
        # Проверяем, что цена указана
        amount = item.get('price')
        if not amount or amount <= 0:
            return jsonify({"error": "Цена не указана или некорректна"}), 400

        # Сохраняем заказ
        order_id = save_order({
            "item_id": item['id'],
            "name": data['name'],
            "email": data['email'],
            "phone": data['phone'],
            "amount": amount,
            "item_name": item['name']
        })

        # Формируем описание (без спецсимволов)
        description = item['name'].replace(' ', '+')

        # Генерируем платёжную ссылку
        payment_url = (
            f"https://pay.pally.info/pay/{PALLY_MERCHANT_ID}"
            f"?amount={amount}"
            f"&description={description}"
            f"&success_url={request.url_root}payment/success?order_id={order_id}"
            f"&fail_url={request.url_root}payment/fail"
        )

        return jsonify({"payment_url": payment_url})
    
    except Exception as e:
        print("Ошибка создания платежа:", e)
        return jsonify({"error": "Не удалось создать платёж"}), 500
    
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            return render_template('admin/login.html', error="Неверный логин или пароль")
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    # Каталог
    catalog = load_catalog()
    catalog_count = len(catalog)

    # Портфолио
    portfolio = load_portfolio()
    portfolio_count = len(portfolio)

    # Обращения
    contacts_path = os.path.join(app.root_path, 'data', 'contacts.json')
    if os.path.exists(contacts_path):
        with open(contacts_path, 'r', encoding='utf-8') as f:
            contacts = json.load(f)
        contacts_count = len(contacts)
        recent_contacts = sorted(contacts, key=lambda x: x['timestamp'], reverse=True)
    else:
        contacts_count = 0
        recent_contacts = []

    # Заказы
    orders_path = os.path.join(app.root_path, 'data', 'orders.json')
    if os.path.exists(orders_path):
        with open(orders_path, 'r', encoding='utf-8') as f:
            orders = json.load(f)
        orders_count = len(orders)
    else:
        orders_count = 0

    return render_template('admin/dashboard.html',
                           catalog_count=catalog_count,
                           portfolio_count=portfolio_count,
                           contacts_count=contacts_count,
                           orders_count=orders_count,
                           recent_contacts=recent_contacts)

# === КАТАЛОГ ===
@app.route('/admin/catalog')
@login_required
def admin_catalog():
    items = load_catalog()
    return render_template('admin/catalog_list.html', items=items)

@app.route('/admin/catalog/new', methods=['GET', 'POST'])
@app.route('/admin/catalog/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def admin_catalog_form(item_id=None):
    item = None
    if item_id:
        item = get_item_by_id(item_id)
        if not item:
            return "Товар не найден", 404

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        material = request.form['material']
        time = request.form['time']
        price = request.form.get('price')
        price = int(price) if price and price.isdigit() else None

        # Обработка изображения
        image_file = request.files.get('image')
        image_filename = None

        if image_file and image_file.filename:
            image_filename = save_image_as_webp(image_file)
            if not image_filename:
                return "Недопустимый формат изображения", 400
        elif item_id and item:
            # При редактировании — оставляем старое изображение
            image_filename = item['image']
        else:
            return "Изображение обязательно", 400

        items = load_catalog()

        if item_id:
            for i, it in enumerate(items):
                if it['id'] == item_id:
                    items[i] = {
                        "id": item_id,
                        "name": name,
                        "description": description,
                        "category": category,
                        "material": material,
                        "time": time,
                        "price": price,
                        "image": image_filename
                    }
                    break
        else:
            new_id = max([it['id'] for it in items], default=0) + 1
            items.append({
                "id": new_id,
                "name": name,
                "description": description,
                "category": category,
                "material": material,
                "time": time,
                "price": price,
                "image": image_filename
            })

        with open(os.path.join(app.root_path, 'data', 'catalog.json'), 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        return redirect(url_for('admin_catalog'))

    return render_template('admin/catalog_form.html', item=item)

@app.route('/admin/catalog/delete/<int:item_id>', methods=['POST'])
@login_required
def admin_catalog_delete(item_id):
    items = load_catalog()
    items = [it for it in items if it['id'] != item_id]
    with open(os.path.join(app.root_path, 'data', 'catalog.json'), 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return redirect(url_for('admin_catalog'))

@app.route('/admin/contacts')
@login_required
def admin_contacts():
    filepath = os.path.join(app.root_path, 'data', 'contacts.json')
    messages = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            messages = json.load(f)
    return render_template('admin/contacts.html', messages=messages)

@app.route('/admin/contacts/delete/<string:timestamp>', methods=['POST'])
@login_required
def admin_contact_delete(timestamp):
    filepath = os.path.join(app.root_path, 'data', 'contacts.json')
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        messages = [m for m in messages if m['timestamp'] != timestamp]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    return redirect(url_for('admin_contacts'))

@app.route('/admin/portfolio')
@login_required
def admin_portfolio():
    projects = load_portfolio()
    return render_template('admin/portfolio_list.html', projects=projects)

@app.route('/admin/orders')
@login_required
def admin_orders():
    return render_template('admin/portfolio_list.html')

@app.route('/admin/portfolio/new', methods=['GET', 'POST'])
@app.route('/admin/portfolio/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def admin_portfolio_form(project_id=None):
    project = None
    if project_id:
        projects = load_portfolio()
        project = next((p for p in projects if p.get('id') == project_id), None)
        if not project:
            return "Работа не найдена", 404

    if request.method == 'POST':
        title = request.form['title']
        client = request.form['client']
        comment = request.form['comment']

        # Обработка изображения
        image_file = request.files.get('image')
        image_filename = None

        if image_file and image_file.filename:
            image_filename = save_image_as_webp(image_file)
            if not image_filename:
                return "Недопустимый формат изображения. Разрешены: JPG, PNG, GIF.", 400
        elif project_id and project:
            # При редактировании — оставляем старое изображение
            image_filename = project['image']
        else:
            return "Изображение обязательно при создании работы.", 400

        # Загружаем текущие данные
        projects = load_portfolio()

        if project_id:
            # Редактирование
            for i, p in enumerate(projects):
                if p.get('id') == project_id:
                    # Опционально: удалить старое изображение
                    old_image = p.get('image')
                    if old_image and old_image != image_filename:
                        old_path = os.path.join(app.root_path, 'static', 'media', old_image)
                        if os.path.exists(old_path):
                            os.remove(old_path)

                    projects[i] = {
                        "id": project_id,
                        "title": title,
                        "client": client,
                        "comment": comment,
                        "image": image_filename
                    }
                    break
        else:
            # Добавление
            new_id = max([p.get('id', 0) for p in projects], default=0) + 1
            projects.append({
                "id": new_id,
                "title": title,
                "client": client,
                "comment": comment,
                "image": image_filename
            })

        # Сохраняем в JSON
        filepath = os.path.join(app.root_path, 'data', 'portfolio.json')
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)

        return redirect(url_for('admin_portfolio'))

    return render_template('admin/portfolio_form.html', project=project)

@app.route('/admin/orders/edit/<string:order_id>', methods=['GET', 'POST'])
@login_required
def admin_order_form(order_id):
    # Загружаем заказы
    orders_path = os.path.join(app.root_path, 'data', 'orders.json')
    if not os.path.exists(orders_path):
        return "Заказ не найден", 404

    with open(orders_path, 'r', encoding='utf-8') as f:
        orders = json.load(f)

    order = next((o for o in orders if o.get('order_id') == order_id), None)
    if not order:
        return "Заказ не найден", 404

    if request.method == 'POST':
        # Обновляем только статус (остальное не редактируется)
        new_status = request.form['status']
        if new_status not in ['pending', 'paid', 'cancelled']:
            new_status = 'pending'

        for o in orders:
            if o['order_id'] == order_id:
                o['status'] = new_status
                if new_status == 'paid' and 'paid_at' not in o:
                    o['paid_at'] = datetime.now().isoformat()
                break

        # Сохраняем
        with open(orders_path, 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)

        return redirect(url_for('admin_orders'))

    return render_template('admin/order_form.html', order=order)

# Удаление портфолио
@app.route('/admin/portfolio/delete/<int:project_id>', methods=['POST'])
@login_required
def admin_portfolio_delete(project_id):
    projects = load_portfolio()
    projects = [p for p in projects if p.get('id') != project_id]
    with open(os.path.join(app.root_path, 'data', 'portfolio.json'), 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)
    return redirect(url_for('admin_portfolio'))

# Удаление заказа
@app.route('/admin/orders/delete/<string:order_id>', methods=['POST'])
@login_required
def admin_order_delete(order_id):
    orders_path = os.path.join(app.root_path, 'data', 'orders.json')
    if os.path.exists(orders_path):
        with open(orders_path, 'r', encoding='utf-8') as f:
            orders = json.load(f)
        orders = [o for o in orders if o.get('order_id') != order_id]
        with open(orders_path, 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)
    return redirect(url_for('admin_orders'))

@app.route('/sitemap.xml')
def sitemapXml():
    return render_template('sitemap.xml')

@app.route('/robots.txt')
def robotxTxt():
    return render_template('robots.txt')

@app.route('/submit', methods=['POST'])
def submit_form():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Валидация (можно расширить)
    if not name or not email or not message:
        return "Все поля обязательны!", 400

    # Загружаем существующие сообщения
    messages = load_messages()

    # Добавляем новое сообщение с временной меткой
    new_entry = {
        "name": name,
        "email": email,
        "message": message,
        "timestamp": datetime.datetime.now().isoformat()
    }
    messages.append(new_entry)

    # Сохраняем обратно в файл
    save_messages(messages)

    # Перенаправляем на главную (или можно показать "спасибо")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)