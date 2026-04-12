# seed.py
# Ejecutar una vez para poblar la base de datos con categorías, productos, mesas y un usuario administrador

from app import create_app
from app.extensions import db
from app.models import Category, Product, Table, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Crear tablas si no existen (ya lo hace create_app, pero por si acaso)
    db.create_all()

    # 1. Crear usuario administrador si no existe
    admin_email = 'admin@example.com'
    admin_username = 'admin'
    admin_password = 'admin123'  # Cambia esto por una contraseña segura en producción

    existing_admin = User.query.filter(
        (User.email == admin_email) | (User.username == admin_username)
    ).first()

    if not existing_admin:
        admin_user = User(
            username=admin_username,
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"✅ Usuario administrador creado: {admin_username} / {admin_password}")
    else:
        # Si ya existe pero no es admin, lo actualizamos
        if not existing_admin.is_admin:
            existing_admin.is_admin = True
            db.session.commit()
            print(f"✅ Usuario '{existing_admin.username}' ahora tiene permisos de administrador.")
        else:
            print(f"ℹ️ El usuario administrador '{existing_admin.username}' ya existe.")

    # 2. Categorías
    categorias = [
        {'name': 'Entradas', 'type': 'comida'},
        {'name': 'Platos Fuertes', 'type': 'comida'},
        {'name': 'Postres', 'type': 'comida'},
        {'name': 'Bebidas', 'type': 'bebida'},
        {'name': 'Cócteles', 'type': 'bebida'},
        {'name': 'Vinos', 'type': 'bebida'},
    ]

    for cat_data in categorias:
        cat = Category.query.filter_by(name=cat_data['name']).first()
        if not cat:
            cat = Category(**cat_data)
            db.session.add(cat)
    db.session.commit()
    print("✅ Categorías creadas/verificadas.")

    # Obtener IDs de categorías
    cat_entradas = Category.query.filter_by(name='Entradas').first()
    cat_platos = Category.query.filter_by(name='Platos Fuertes').first()
    cat_postres = Category.query.filter_by(name='Postres').first()
    cat_bebidas = Category.query.filter_by(name='Bebidas').first()
    cat_cocteles = Category.query.filter_by(name='Cócteles').first()
    cat_vinos = Category.query.filter_by(name='Vinos').first()

    # 3. Productos de muestra
    # Productos de muestra con imágenes variadas
    productos = [
        # Entradas
        {'name': 'Pan de Masa Madre con Mantequilla de Hierbas', 'description': 'Pan artesanal de fermentación lenta, servido con mantequilla batida de romero y ajo.', 'price': 6.50, 'category': cat_entradas, 'image_url': 'https://images.pexels.com/photos/209206/pexels-photo-209206.jpeg?auto=compress&cs=tinysrgb&w=600', 'is_signature': True},
        {'name': 'Aceitunas Marinadas', 'description': 'Mezcla de aceitunas griegas con piel de naranja, tomillo y aceite de oliva virgen extra.', 'price': 5.00, 'category': cat_entradas, 'image_url': 'https://images.pexels.com/photos/315755/pexels-photo-315755.jpeg?auto=compress&cs=tinysrgb&w=600'},
        {'name': 'Croquetas de Jamón Ibérico', 'description': 'Croquetas cremosas de jamón ibérico con un toque de nuez moscada.', 'price': 8.00, 'category': cat_entradas, 'image_url': 'https://images.pexels.com/photos/566566/pexels-photo-566566.jpeg?auto=compress&cs=tinysrgb&w=600'},
        # Platos Fuertes
        {'name': 'Risotto de Hongos Silvestres', 'description': 'Arroz arbóreo con mezcla de hongos de temporada, queso parmesano y aceite de trufa.', 'price': 18.50, 'category': cat_platos, 'image_url': 'https://images.pexels.com/photos/803963/pexels-photo-803963.jpeg?auto=compress&cs=tinysrgb&w=600', 'is_signature': True},
        {'name': 'Salmón a la Parrilla', 'description': 'Filete de salmón orgánico con costra de hierbas, servido con puré de coliflor y espárragos.', 'price': 22.00, 'category': cat_platos, 'image_url': 'https://images.pexels.com/photos/46239/salmon-dish-food-meal-46239.jpeg?auto=compress&cs=tinysrgb&w=600'},
        {'name': 'Hamburguesa Artesanal', 'description': 'Blend de res angus, queso cheddar añejo, cebolla caramelizada, pepinillos y salsa secreta en pan brioche.', 'price': 15.50, 'category': cat_platos, 'image_url': 'https://images.pexels.com/photos/2983098/pexels-photo-2983098.jpeg?auto=compress&cs=tinysrgb&w=600'},
        {'name': 'Pasta al Pesto de Albahaca', 'description': 'Linguini fresco con pesto genovés, tomates cherry confitados y piñones tostados.', 'price': 14.00, 'category': cat_platos, 'image_url': 'https://images.pexels.com/photos/1437267/pexels-photo-1437267.jpeg?auto=compress&cs=tinysrgb&w=600'},
        # Postres
        {'name': 'Tarta de Chocolate y Caramelo Salado', 'description': 'Base de galleta de cacao, ganache de chocolate oscuro y caramelo salado.', 'price': 7.50, 'category': cat_postres, 'image_url': 'https://images.pexels.com/photos/291528/pexels-photo-291528.jpeg?auto=compress&cs=tinysrgb&w=600', 'is_offer': True},
        {'name': 'Crumble de Manzana', 'description': 'Manzanas asadas con canela y crumble de avena, servido con helado de vainilla.', 'price': 6.50, 'category': cat_postres, 'image_url': 'https://images.pexels.com/photos/2067396/pexels-photo-2067396.jpeg?auto=compress&cs=tinysrgb&w=600'},
        # Bebidas
        {'name': 'Limonada de Jengibre y Menta', 'description': 'Refrescante limonada casera con jengibre fresco y menta.', 'price': 3.50, 'category': cat_bebidas, 'image_url': 'https://images.pexels.com/photos/4110226/pexels-photo-4110226.jpeg?auto=compress&cs=tinysrgb&w=600'},
        {'name': 'Té Helado de Hibisco', 'description': 'Infusión fría de flor de jamaica con un toque de limón.', 'price': 3.00, 'category': cat_bebidas, 'image_url': 'https://images.pexels.com/photos/5946987/pexels-photo-5946987.jpeg?auto=compress&cs=tinysrgb&w=600'},
        {'name': 'Café de Especialidad', 'description': 'Café de origen único preparado en prensa francesa.', 'price': 2.80, 'category': cat_bebidas, 'image_url': 'https://images.pexels.com/photos/302899/pexels-photo-302899.jpeg?auto=compress&cs=tinysrgb&w=600'},
        # Cócteles
        {'name': 'Rosemary Smoked Old Fashioned', 'description': 'Bourbon infusionado con humo de romero, azúcar morena y amargo de angostura.', 'price': 12.00, 'category': cat_cocteles, 'image_url': 'https://images.pexels.com/photos/5947038/pexels-photo-5947038.jpeg?auto=compress&cs=tinysrgb&w=600', 'is_signature': True},
        {'name': 'Gin Tónica de Pepino y Eneldo', 'description': 'Ginebra premium, tónica artesanal, pepino y eneldo fresco.', 'price': 11.00, 'category': cat_cocteles, 'image_url': 'https://images.pexels.com/photos/5947068/pexels-photo-5947068.jpeg?auto=compress&cs=tinysrgb&w=600'},
        {'name': 'Margarita de Mango y Habanero', 'description': 'Tequila reposado, licor de naranja, puré de mango y un toque picante.', 'price': 10.50, 'category': cat_cocteles, 'image_url': 'https://images.pexels.com/photos/5947108/pexels-photo-5947108.jpeg?auto=compress&cs=tinysrgb&w=600'},
        # Vinos
        {'name': 'Vino Tinto Malbec', 'description': 'Copa de Malbec argentino, notas de ciruela y vainilla.', 'price': 8.00, 'category': cat_vinos, 'image_url': 'https://images.pexels.com/photos/2912108/pexels-photo-2912108.jpeg?auto=compress&cs=tinysrgb&w=600'},
        {'name': 'Vino Blanco Sauvignon Blanc', 'description': 'Fresco y cítrico, ideal para mariscos.', 'price': 7.50, 'category': cat_vinos, 'image_url': 'https://images.pexels.com/photos/5947005/pexels-photo-5947005.jpeg?auto=compress&cs=tinysrgb&w=600'},
    ]

    for prod_data in productos:
        prod = Product.query.filter_by(name=prod_data['name']).first()
        if not prod:
            prod = Product(**prod_data)
            db.session.add(prod)
    db.session.commit()
    print("✅ Productos de muestra creados/verificados.")

    # 4. Crear mesas de ejemplo (1 al 10)
    for i in range(1, 11):
        if not Table.query.filter_by(number=i).first():
            db.session.add(Table(number=i, capacity=4))
    db.session.commit()
    print("✅ Mesas creadas/verificadas (1-10).")

    print("\n🎉 Base de datos poblada exitosamente.")
    print("   Usuario administrador: admin@example.com / admin123")
    print("   Ahora puedes iniciar sesión y acceder a /admin/gestion-pedidos")