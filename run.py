from app import create_app, db
import os

app = create_app()

with app.app_context():
    db.create_all()
    # Ejecutar seed solo si la base está vacía
    from app.models import User
    if User.query.count() == 0:
        from seed import seed_database
        seed_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)