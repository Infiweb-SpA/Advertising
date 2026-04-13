from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Order, OrderItem, Table, Product, Category
from app.extensions import db
from functools import wraps
from datetime import datetime, timedelta
from flask import Response, stream_with_context, jsonify
import json
import time

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# --- Dashboard (ruta raíz) ---
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    from datetime import datetime, timedelta
    
    today = datetime.utcnow().date()
    since_date = datetime.utcnow() - timedelta(days=30)
    
    # Pedidos de hoy
    orders_today = Order.query.filter(Order.created_at >= today).all()
    
    # Todos los pedidos recientes
    all_orders = Order.query.filter(Order.created_at >= since_date).all()
    
    # Ingresos de hoy
    total_revenue_today = db.session.query(db.func.sum(Order.total)).filter(
        Order.created_at >= today
    ).scalar() or 0.0
    
    # CONTADORES POR ESTADO
    orders_received_count = len([o for o in all_orders if o.status == 'received'])
    orders_preparing_count = len([o for o in all_orders if o.status == 'preparing'])
    orders_ready_count = len([o for o in all_orders if o.status == 'ready'])
    orders_served_count = len([o for o in all_orders if o.status == 'served'])
    orders_completed_count = len([o for o in all_orders if o.status == 'completed'])
    
    # CONTADORES POR TIPO (todos los pedidos activos: received, preparing, ready)
    active_statuses = ['received', 'preparing', 'ready']
    orders_for_dine_in = len([o for o in all_orders if o.order_type == 'dine_in' and o.status in active_statuses])
    orders_for_takeaway = len([o for o in all_orders if o.order_type == 'takeaway' and o.status in active_statuses])
    
    # Pedidos activos totales
    active_orders = orders_received_count + orders_preparing_count + orders_ready_count
    
    return render_template('admin/dashboard.html',
                           total_orders_today=len(orders_today),
                           total_orders_all=len(all_orders),
                           total_revenue_today=total_revenue_today,
                           active_orders=active_orders,
                           orders_received_count=orders_received_count,
                           orders_preparing_count=orders_preparing_count,
                           orders_ready_count=orders_ready_count,
                           orders_served_count=orders_served_count,
                           orders_completed_count=orders_completed_count,
                           orders_for_dine_in=orders_for_dine_in,
                           orders_for_takeaway=orders_for_takeaway)

# --- Endpoint para datos del dashboard (JSON) ---
@admin_bp.route('/dashboard-data')
@login_required
@admin_required
def dashboard_data():
    today = datetime.utcnow().date()
    since_date = datetime.utcnow() - timedelta(days=30)
    
    all_orders = Order.query.filter(Order.created_at >= since_date).all()
    orders_today = Order.query.filter(Order.created_at >= today).all()
    
    total_revenue_today = db.session.query(db.func.sum(Order.total)).filter(
        Order.created_at >= today
    ).scalar() or 0.0
    
    orders_received_count = len([o for o in all_orders if o.status == 'received'])
    orders_preparing_count = len([o for o in all_orders if o.status == 'preparing'])
    orders_ready_count = len([o for o in all_orders if o.status == 'ready'])
    orders_completed_count = len([o for o in all_orders if o.status == 'completed'])
    
    # Contadores por tipo (todos los pedidos activos)
    active_statuses = ['received', 'preparing', 'ready']
    orders_for_dine_in = len([o for o in all_orders if o.order_type == 'dine_in' and o.status in active_statuses])
    orders_for_takeaway = len([o for o in all_orders if o.order_type == 'takeaway' and o.status in active_statuses])
    
    active_orders = orders_received_count + orders_preparing_count + orders_ready_count
    
    return jsonify({
        'total_orders_today': len(orders_today),
        'total_orders_all': len(all_orders),
        'total_revenue_today': total_revenue_today,
        'active_orders': active_orders,
        'orders_received_count': orders_received_count,
        'orders_preparing_count': orders_preparing_count,
        'orders_ready_count': orders_ready_count,
        'orders_completed_count': orders_completed_count,
        'orders_for_dine_in': orders_for_dine_in,
        'orders_for_takeaway': orders_for_takeaway
    })

# --- SSE Stream para actualizaciones en tiempo real ---
@admin_bp.route('/dashboard-stream')
@login_required
@admin_required
def dashboard_stream():
    def event_stream():
        while True:
            today = datetime.utcnow().date()
            since_date = datetime.utcnow() - timedelta(days=30)
            
            all_orders = Order.query.filter(Order.created_at >= since_date).all()
            orders_today = Order.query.filter(Order.created_at >= today).all()
            
            total_revenue_today = db.session.query(db.func.sum(Order.total)).filter(
                Order.created_at >= today
            ).scalar() or 0.0
            
            orders_received_count = len([o for o in all_orders if o.status == 'received'])
            orders_preparing_count = len([o for o in all_orders if o.status == 'preparing'])
            orders_ready_count = len([o for o in all_orders if o.status == 'ready'])
            orders_completed_count = len([o for o in all_orders if o.status == 'completed'])
            
            # Contadores por tipo (todos los pedidos activos)
            active_statuses = ['received', 'preparing', 'ready']
            orders_for_dine_in = len([o for o in all_orders if o.order_type == 'dine_in' and o.status in active_statuses])
            orders_for_takeaway = len([o for o in all_orders if o.order_type == 'takeaway' and o.status in active_statuses])
            
            active_orders = orders_received_count + orders_preparing_count + orders_ready_count
            
            data = {
                'total_orders_today': len(orders_today),
                'total_orders_all': len(all_orders),
                'total_revenue_today': float(total_revenue_today),
                'active_orders': active_orders,
                'orders_received_count': orders_received_count,
                'orders_preparing_count': orders_preparing_count,
                'orders_ready_count': orders_ready_count,
                'orders_completed_count': orders_completed_count,
                'orders_for_dine_in': orders_for_dine_in,
                'orders_for_takeaway': orders_for_takeaway
            }
            
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(5)
    
    return Response(stream_with_context(event_stream()), 
                    mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'X-Accel-Buffering': 'no'
                    })

# --- Gestión de pedidos (mesa + takeaway) ---
@admin_bp.route('/gestion-pedidos')
@login_required
@admin_required
def gestion_pedidos():
    since_date = datetime.utcnow() - timedelta(days=7)
    all_recent_orders = Order.query.filter(Order.created_at >= since_date).order_by(Order.created_at.desc()).all()
    
    dine_in_orders = [o for o in all_recent_orders if o.order_type == 'dine_in']
    takeaway_orders = [o for o in all_recent_orders if o.order_type == 'takeaway']
    
    if not all_recent_orders:
        all_orders = Order.query.order_by(Order.created_at.desc()).limit(50).all()
        dine_in_orders = [o for o in all_orders if o.order_type == 'dine_in']
        takeaway_orders = [o for o in all_orders if o.order_type == 'takeaway']
    
    active_orders_count = len([o for o in all_recent_orders if o.status in ['received', 'preparing', 'ready']])
    tables = Table.query.all()
    now = datetime.utcnow()

    orders_received_count = len([o for o in all_recent_orders if o.status == 'received'])
    orders_preparing_count = len([o for o in all_recent_orders if o.status == 'preparing'])
    orders_ready_count = len([o for o in all_recent_orders if o.status == 'ready'])
    orders_served_count = len([o for o in all_recent_orders if o.status == 'served'])
    orders_completed_count = len([o for o in all_recent_orders if o.status == 'completed'])
    
    return render_template('gestion_pedidos.html', 
                           dine_in_orders=dine_in_orders, 
                           takeaway_orders=takeaway_orders,
                           tables=tables,
                           active_orders_count=active_orders_count,
                           orders_received_count=orders_received_count,
                           orders_preparing_count=orders_preparing_count,
                           orders_ready_count=orders_ready_count,
                           orders_served_count=orders_served_count,
                           orders_completed_count=orders_completed_count,
                           now=now)

# --- Vista dedicada para pedidos takeaway ---
@admin_bp.route('/takeaway')
@login_required
@admin_required
def takeaway_orders_view():
    since_date = datetime.utcnow() - timedelta(days=7)
    takeaway_orders = Order.query.filter_by(order_type='takeaway')\
                                 .filter(Order.created_at >= since_date)\
                                 .order_by(Order.created_at.desc()).all()
    now = datetime.utcnow()
    return render_template('admin/takeaway.html',
                           takeaway_orders=takeaway_orders,
                           now=now)

# --- Editor de menú ---
@admin_bp.route('/menu-editor')
@login_required
@admin_required
def menu_editor():
    categories = Category.query.all()
    products = Product.query.order_by(Product.category_id, Product.name).all()
    return render_template('admin/menu_editor.html',
                           categories=categories,
                           products=products)

# --- Configuraciones ---
@admin_bp.route('/configuraciones', methods=['GET', 'POST'])
@login_required
@admin_required
def configuraciones():
    from app.models import Setting
    if request.method == 'POST':
        Setting.set('restaurant_name', request.form.get('restaurant_name', ''))
        Setting.set('business_hours', request.form.get('business_hours', ''))
        Setting.set('tax_rate', request.form.get('tax_rate', '19'))
        Setting.set('currency', request.form.get('currency', 'USD'))
        Setting.set('address', request.form.get('address', ''))
        Setting.set('phone', request.form.get('phone', ''))
        flash('Configuraciones guardadas correctamente.', 'success')
        return redirect(url_for('admin.configuraciones'))
    
    context = {
        'restaurant_name': Setting.get('restaurant_name', 'La editorial culinaria'),
        'business_hours': Setting.get('business_hours', 'Lun-Vie 07:00 - 21:00'),
        'tax_rate': Setting.get('tax_rate', '19'),
        'currency': Setting.get('currency', 'USD'),
        'address': Setting.get('address', 'Calle Principal 123, Ciudad'),
        'phone': Setting.get('phone', '+1 555 123 4567'),
    }
    return render_template('admin/configuraciones.html', **context)

# --- Actualizar estado de pedido (POST) ---
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

# --- Crear nuevo producto ---
@admin_bp.route('/menu-editor/producto/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def create_product():
    if request.method == 'POST':
        try:
            product = Product(
                name=request.form.get('name', '').strip(),
                description=request.form.get('description', '').strip(),
                price=float(request.form.get('price', 0)),
                category_id=int(request.form.get('category_id')),
                available=request.form.get('available') == 'on',
                is_signature=request.form.get('is_signature') == 'on',
                is_offer=request.form.get('is_offer') == 'on',
                image_url=request.form.get('image_url', '').strip()
            )
            db.session.add(product)
            db.session.commit()
            flash(f'Producto "{product.name}" creado exitosamente.', 'success')
            return redirect(url_for('admin.menu_editor'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear producto: {str(e)}', 'danger')
            return redirect(url_for('admin.menu_editor'))
    
    return redirect(url_for('admin.menu_editor'))

# --- Editar producto ---
@admin_bp.route('/menu-editor/producto/<int:product_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            product.name = request.form.get('name', '').strip()
            product.description = request.form.get('description', '').strip()
            product.price = float(request.form.get('price', 0))
            product.category_id = int(request.form.get('category_id'))
            product.available = request.form.get('available') == 'on'
            product.is_signature = request.form.get('is_signature') == 'on'
            product.is_offer = request.form.get('is_offer') == 'on'
            product.image_url = request.form.get('image_url', '').strip()
            
            db.session.commit()
            flash(f'Producto "{product.name}" actualizado exitosamente.', 'success')
            return redirect(url_for('admin.menu_editor'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar producto: {str(e)}', 'danger')
            return redirect(url_for('admin.menu_editor'))
    
    return redirect(url_for('admin.menu_editor'))

# --- Eliminar producto ---
@admin_bp.route('/menu-editor/producto/<int:product_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash(f'Producto "{product.name}" eliminado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
    return redirect(url_for('admin.menu_editor'))