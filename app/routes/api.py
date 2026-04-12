from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Order, OrderItem, Product, Table
from app.extensions import db
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/submit_order', methods=['POST'])
def submit_order():
    data = request.get_json()
    cart = data.get('cart')
    table_number = data.get('table_number')
    order_type = data.get('order_type', 'dine_in')
    
    if not cart:
        return jsonify({'error': 'Carrito vacío'}), 400
    
    # Buscar mesa si es para comer en el local
    table = None
    if order_type == 'dine_in' and table_number:
        table = Table.query.filter_by(number=table_number).first()
        if not table:
            return jsonify({'error': 'Número de mesa inválido'}), 400
    
    # Crear pedido
    order = Order(
        order_type=order_type,
        table_id=table.id if table else None,
        user_id=current_user.id if current_user.is_authenticated else None,
        status='received',
        created_at=datetime.utcnow()
    )
    db.session.add(order)
    db.session.flush()  # Para obtener order.id
    
    total = 0
    for item in cart.values():
        product = Product.query.get(item['product_id'])
        if product:
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item['quantity'],
                unit_price=product.price
            )
            db.session.add(order_item)
            total += product.price * item['quantity']
    
    order.total = total
    db.session.commit()
    
    return jsonify({'success': True, 'order_id': order.id, 'total': total})

@api_bp.route('/products')
def get_products():
    products = Product.query.filter_by(available=True).all()
    result = []
    for p in products:
        result.append({
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'description': p.description,
            'image_url': p.image_url,
            'category': p.category.name if p.category else None
        })
    return jsonify(result)