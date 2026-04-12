from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Order, OrderItem, Table, Product, Category
from app.extensions import db
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    return redirect(url_for('admin.gestion_pedidos'))

@admin_bp.route('/gestion-pedidos')
@login_required
@admin_required
def gestion_pedidos():
    # Obtener pedidos activos
    dine_in_orders = Order.query.filter_by(order_type='dine_in').filter(Order.status.in_(['received', 'preparing', 'ready'])).all()
    takeaway_orders = Order.query.filter_by(order_type='takeaway').filter(Order.status.in_(['received', 'preparing', 'ready'])).all()
    tables = Table.query.all()
    return render_template('gestion_pedidos.html', 
                           dine_in_orders=dine_in_orders, 
                           takeaway_orders=takeaway_orders,
                           tables=tables)

@admin_bp.route('/update-order-status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ['received', 'preparing', 'ready', 'served', 'completed']:
        order.status = new_status
        db.session.commit()
        flash(f'Pedido #{order.id} actualizado a {new_status}', 'success')
    return redirect(url_for('admin.gestion_pedidos'))

# Más rutas para CRUD de productos, categorías, etc.