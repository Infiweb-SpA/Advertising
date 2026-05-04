# seed.py
import os
import sys
from werkzeug.security import generate_password_hash

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Category, Product, Table, User


def seed_database():
    print("🌱 Iniciando seeding Hard Bar...")

    app = create_app()

    with app.app_context():
        db.create_all()

        # ==============================
        # USUARIO ADMIN
        # ==============================
        admin_email = "admin@hardbar.cl"
        admin_username = "admin"
        admin_password = "admin123"

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
            print("✅ Admin creado")

        # ==============================
        # CATEGORÍAS
        # ==============================
        categorias = [
            {"name": "Seminarios de Compartir", "type": "comida"},
            {"name": "Combos Hard Bar", "type": "comida"},
            {"name": "Combos Completos", "type": "comida"},
            {"name": "Desayunos", "type": "comida"},
            {"name": "Arma tu Desayuno", "type": "comida"},
            {"name": "Platos de la Casa", "type": "comida"},
            {"name": "Menú de Niño", "type": "comida"},
            {"name": "Coctelería", "type": "bebida"},
            {"name": "Cervezas", "type": "bebida"},
            {"name": "Vinos y Espumantes", "type": "bebida"},
            {"name": "Destilados", "type": "bebida"},
        ]

        for cat in categorias:
            if not Category.query.filter_by(name=cat["name"]).first():
                db.session.add(Category(**cat))

        db.session.commit()

        def cat(nombre):
            return Category.query.filter_by(name=nombre).first()

        # ==============================
        # PRODUCTOS
        # ==============================

        productos = [

            # ================= SEMINARIOS =================
            {"name": "Tabla Hard Bar (2 personas)", "price": 16990, "category": cat("Seminarios de Compartir")},
            {"name": "Tabla Hard Bar (4 personas)", "price": 22990, "category": cat("Seminarios de Compartir")},

            {"name": "Tabla Suprem (2 personas)", "price": 16990, "category": cat("Seminarios de Compartir")},
            {"name": "Tabla Suprem (4 personas)", "price": 22990, "category": cat("Seminarios de Compartir")},

            {"name": "Super Hard Premium (2 personas)", "price": 20990, "category": cat("Seminarios de Compartir")},
            {"name": "Super Hard Premium (4 personas)", "price": 36990, "category": cat("Seminarios de Compartir")},

            {"name": "Papas Bravas", "price": 10990, "category": cat("Seminarios de Compartir")},
            {"name": "Chorrillana Tradicional", "price": 15990, "category": cat("Seminarios de Compartir")},
            {"name": "Tabla Vegetariana", "price": 10990, "category": cat("Seminarios de Compartir")},

            # ================= COMBOS =================
            {"name": "Hamburguesa Hard Bar", "price": 6990, "category": cat("Combos Hard Bar")},
            {"name": "Hamburguesa Italiana", "price": 6590, "category": cat("Combos Hard Bar")},
            {"name": "Hamburguesa Posgrado", "price": 7990, "category": cat("Combos Hard Bar")},
            {"name": "Mechada Italiana", "price": 6990, "category": cat("Combos Hard Bar")},
            {"name": "Mechada Chacarera", "price": 7990, "category": cat("Combos Hard Bar")},
            {"name": "Mechada Luco", "price": 5990, "category": cat("Combos Hard Bar")},

            # ================= COMBOS COMPLETOS =================
            {"name": "Hot Dog Completo", "price": 3590, "category": cat("Combos Completos")},
            {"name": "Italiano Completo", "price": 3990, "category": cat("Combos Completos")},
            {"name": "Dinámico Completo", "price": 4990, "category": cat("Combos Completos")},
            {"name": "Hass Mechada", "price": 4990, "category": cat("Combos Completos")},

            # ================= DESAYUNOS =================
            {"name": "Desayuno Hard Bar", "price": 6990, "category": cat("Desayunos")},
            {"name": "Desayuno Campestre", "price": 5990, "category": cat("Desayunos")},
            {"name": "Desayuno Premium", "price": 7990, "category": cat("Desayunos")},

            # ================= ARMA TU DESAYUNO =================
            {"name": "Té o Café clásico", "price": 1990, "category": cat("Arma tu Desayuno")},
            {"name": "Café máquina chico", "price": 2390, "category": cat("Arma tu Desayuno")},
            {"name": "Café máquina mediano", "price": 2690, "category": cat("Arma tu Desayuno")},
            {"name": "Café máquina grande", "price": 2990, "category": cat("Arma tu Desayuno")},
            {"name": "Jugo natural", "price": 3490, "category": cat("Arma tu Desayuno")},
            {"name": "Bebida Express", "price": 1990, "category": cat("Arma tu Desayuno")},
            {"name": "Trozo de Torta", "price": 3490, "category": cat("Arma tu Desayuno")},
            {"name": "Pie de Limón / Frambuesa", "price": 2590, "category": cat("Arma tu Desayuno")},
            {"name": "Waffles", "price": 2990, "category": cat("Arma tu Desayuno")},
            {"name": "Empanada de Horno", "price": 2990, "category": cat("Arma tu Desayuno")},

            # ================= PLATOS DE LA CASA =================
            {"name": "Cordero Escabechado", "price": 15990, "category": cat("Platos de la Casa")},
            {"name": "Carne de Res al Vino", "price": 15990, "category": cat("Platos de la Casa")},
            {"name": "Trucha a la Plancha", "price": 14990, "category": cat("Platos de la Casa")},
            {"name": "Trucha Cordillerana", "price": 15990, "category": cat("Platos de la Casa")},
            {"name": "Filete de Pollo a la Plancha", "price": 10900, "category": cat("Platos de la Casa")},
            {"name": "Chuleta a la Plancha", "price": 12990, "category": cat("Platos de la Casa")},
            {"name": "Chuleta Rosa Mosqueta", "price": 13900, "category": cat("Platos de la Casa")},
            {"name": "Pastel de Choclo", "price": 10900, "category": cat("Platos de la Casa")},
            {"name": "Espagueti con Salsa", "price": 7990, "category": cat("Platos de la Casa")},
            {"name": "Milanesa de Pollo", "price": 11990, "category": cat("Platos de la Casa")},

            # ================= MENU NIÑO =================
            {"name": "Espagueti con Vienesa y Huevo", "price": 4990, "category": cat("Menú de Niño")},
            {"name": "Nuggets con Papas", "price": 4990, "category": cat("Menú de Niño")},

            # ================= CERVEZAS =================
            {"name": "Shop Stella / Heineken", "price": 3990, "category": cat("Cervezas")},
            {"name": "Cerveza Artesanal Llaima", "price": 4990, "category": cat("Cervezas")},
            {"name": "Cerveza Corona", "price": 3990, "category": cat("Cervezas")},
            {"name": "Cerveza Royal", "price": 3500, "category": cat("Cervezas")},

            # ================= VINOS =================
            {"name": "Copa Espumante", "price": 3690, "category": cat("Vinos y Espumantes")},
            {"name": "Botella Espumante", "price": 12990, "category": cat("Vinos y Espumantes")},
            {"name": "Vino Reserva", "price": 14990, "category": cat("Vinos y Espumantes")},
            {"name": "Vino Gran Reserva", "price": 28990, "category": cat("Vinos y Espumantes")},
            {"name": "Copa Vino Selección", "price": 2990, "category": cat("Vinos y Espumantes")},

            # ================= COCTELERÍA =================
            {"name": "Ramazzotti Rosato", "price": 5990, "category": cat("Coctelería")},
            {"name": "Ramazzotti Violeta", "price": 6490, "category": cat("Coctelería")},
            {"name": "Aperol Spritz", "price": 5990, "category": cat("Coctelería")},
            {"name": "Margarita", "price": 5490, "category": cat("Coctelería")},
            {"name": "Piña Colada", "price": 4990, "category": cat("Coctelería")},
            {"name": "Tequila Sunrise", "price": 5490, "category": cat("Coctelería")},
            {"name": "Blue Lagoon", "price": 5490, "category": cat("Coctelería")},
            {"name": "Mojito", "price": 4990, "category": cat("Coctelería")},
            {"name": "Borgoña", "price": 4500, "category": cat("Coctelería")},

            # ================= DESTILADOS =================
            {"name": "Pisco + Bebida", "price": 5990, "category": cat("Destilados")},
            {"name": "Whisky + Bebida", "price": 6990, "category": cat("Destilados")},
            {"name": "Whisky a la Roca", "price": 4990, "category": cat("Destilados")},
            {"name": "Vodka Naranja", "price": 3990, "category": cat("Destilados")},
            {"name": "Shot Tequila (3)", "price": 6990, "category": cat("Destilados")},
        ]

        creados = 0
        for prod in productos:
            if not Product.query.filter_by(name=prod["name"]).first():
                db.session.add(Product(**prod))
                creados += 1

        db.session.commit()

        print(f"✅ {creados} productos creados.")
        print("🎉 Base de datos Hard Bar lista!")


def main():
    try:
        seed_database()
    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    main()