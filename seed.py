# seed.py (ejecutar una vez)
from app import create_app
from app.extensions import db
from app.models import User, Category, Product, Table
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Crear admin
    admin = User(username='admin', email='admin@example.com', 
                 password_hash=generate_password_hash('admin123'), is_admin=True)
    db.session.add(admin)
    
    # Categorías
    cat_comida = Category(name='Comida', type='comida')
    cat_bebida = Category(name='Bebestibles', type='bebida')
    db.session.add_all([cat_comida, cat_bebida])
    
    # Productos (ejemplos)
    productos = [
        Product(name='Wild Yeast Sourdough', description='Fermentado 48h...', price=12.00, 
                category=cat_comida, is_signature=True, image_url='...'),
        Product(name='Heirloom Garden Plate', price=18.50, category=cat_comida),
        # ... agregar los demás
    ]
    db.session.add_all(productos)
    
    # Mesas
    for i in range(1, 13):
        db.session.add(Table(number=i))
    
    db.session.commit()
    print("Base de datos inicializada.")