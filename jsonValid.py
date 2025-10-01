import json
import os
from app import app
import uuid
import datetime
from PIL import Image

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