from flask import Flask
from app.config import Config
from app.extensions import db, login_manager
from app.models import Setting



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)

    # ✅ Definir user_loader para Flask-Login
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.context_processor
    def inject_settings():
        return {
            'site_name': Setting.get('restaurant_name', 'La editorial culinaria'),
            'business_hours': Setting.get('business_hours', 'Lun-Vie 07:00 - 21:00'),
            'address': Setting.get('address', 'Calle Principal 123, Ciudad'),
            'phone': Setting.get('phone', '+1 555 123 4567'),
            'currency': Setting.get('currency', 'USD'),
            'tax_rate': Setting.get('tax_rate', '19')
        }

    # Registrar blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Crear tablas si no existen (solo desarrollo)
    with app.app_context():
        db.create_all()

    return app