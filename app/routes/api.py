from flask import Blueprint, request, jsonify
from flask_login import current_user
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
    if order_type == 'dine_in':
        if not table_number:
            return jsonify({'error': 'Número de mesa requerido para pedidos en mesa'}), 400
        try:
            table_number_int = int(table_number)
        except ValueError:
            return jsonify({'error': 'Número de mesa inválido'}), 400
        table = Table.query.filter_by(number=table_number_int).first()
        if not table:
            # Crear la mesa automáticamente si no existe (opcional)
            table = Table(number=table_number_int, status='occupied')
            db.session.add(table)
            db.session.flush()
    else:
        # Para takeaway, no se requiere mesa, pero podemos asignar un número ficticio o null
        table = None
    
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
        product = Product.query.get(item['id'])
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