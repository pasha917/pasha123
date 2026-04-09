from app import app, db, User
from passlib.hash import pbkdf2_sha256

with app.app_context():
    email = 'deliveryuser@gmail.com'
    user = User.query.filter_by(email=email).first()
    if user:
        print('exists')
    else:
        user = User(name='Delivery Gmail', email=email, role='delivery', vehicle_number='DL-01-2345', address='Delhi')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print('created')
