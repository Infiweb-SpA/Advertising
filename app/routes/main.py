from flask import Blueprint, flash, redirect, render_template, request, session, jsonify, url_for
from app.models import Product, Category, Order, OrderItem, Table
from app.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/carta')
def carta():
    # Obtener productos por categoría para pasar al template
    categories = Category.query.all()
    products = Product.query.filter_by(available=True).all()
    return render_template('carta.html', categories=categories, products=products)

@main_bp.route('/info')
def info():
    return render_template('info.html')

# API simple para agregar items al carrito (usando sesión Flask)
@main_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404

    cart = session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': product.price,
            'quantity': quantity
        }
    session['cart'] = cart
    return jsonify({'cart': cart, 'total': sum(item['price']*item['quantity'] for item in cart.values())})

@main_bp.route('/cart')
def view_cart():
    # Redirigir a la carta, ya que el carrito se maneja en el sidebar
    flash('El carrito ahora se gestiona directamente en la carta.', 'info')
    return redirect(url_for('main.carta'))

@main_bp.context_processor
def inject_cart_count():
    cart = session.get('cart', {})
    count = sum(item['quantity'] for item in cart.values())
    return dict(cart_count=count)



@main_bp.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
        flash('Item removed from cart.', 'info')
    return redirect(url_for('main.view_cart'))