import os
import re
import random
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from passlib.hash import pbkdf2_sha256
from sqlalchemy import inspect, text
from dotenv import load_dotenv
from twilio.rest import Client
import razorpay
import openai
from flask_cors import CORS
import pymongo

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hackathon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@rapidodelivery.app')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['GOOGLE_MAPS_API_KEY'] = os.environ.get('GOOGLE_MAPS_API_KEY', '')
DEBUG_OTP = os.environ.get('DEBUG_OTP', 'false').lower() == 'true'

# OpenAI configuration
openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY', ''))

# MongoDB configuration
mongo_client = pymongo.MongoClient("mongodb+srv://pashay119_db_user:sToLfsH5Y0JpCgz2@cluster0.fmmkvqf.mongodb.net/hackathon_ai")
mongo_db = mongo_client['hackathon_ai']

# Razorpay configuration
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_your_key_id')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'your_key_secret')
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

mail = Mail(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

ROLE_CUSTOMER = 'customer'
ROLE_SHOPKEEPER = 'shopkeeper'
ROLE_DELIVERY = 'delivery'
ROLE_ADMIN = 'admin'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    shop_name = db.Column(db.String(120))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(40))
    vehicle_number = db.Column(db.String(40))
    otp = db.Column(db.String(10))
    otp_expiry = db.Column(db.DateTime)
    tracking_code = db.Column(db.String(6), unique=True)
    # Location tracking for delivery persons
    current_lat = db.Column(db.Float)
    current_lng = db.Column(db.Float)
    location_updated_at = db.Column(db.DateTime)
    is_sharing_location = db.Column(db.Boolean, default=False)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

    def set_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Float, default=4.6)
    scanner_filename = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    owner = db.relationship('User', backref='shops')

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, default=4.5)
    shop = db.relationship('Shop', backref='items')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    delivery_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code = db.Column(db.String(6), nullable=False)
    status = db.Column(db.String(40), default='New')
    payment_method = db.Column(db.String(30), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    eta = db.Column(db.DateTime)
    pickup_lat = db.Column(db.Float)
    pickup_lng = db.Column(db.Float)
    delivery_lat = db.Column(db.Float)
    delivery_lng = db.Column(db.Float)
    razorpay_order_id = db.Column(db.String(100))
    razorpay_payment_id = db.Column(db.String(100))
    customer = db.relationship('User', foreign_keys=[customer_id])
    shop = db.relationship('Shop')
    delivery = db.relationship('User', foreign_keys=[delivery_id])
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    item = db.relationship('Item')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_otp():
    return ''.join(random.choices(string.digits, k=6))

def create_tracking_code():
    return ''.join(random.choices(string.digits, k=4))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def is_valid_email(email):
    if not email:
        return False
    email = email.strip().lower()
    pattern = r'^[A-Za-z0-9._%+-]+@gmail\.com$'
    return bool(re.match(pattern, email))

def is_valid_name(name):
    return bool(re.fullmatch(r"[A-Za-z ]+", name.strip()))

def is_valid_password(password):
    if not password or len(password) < 8:
        return False
    rules = [
        r"[A-Z]",
        r"[a-z]",
        r"\d",
        r"[^A-Za-z0-9]"
    ]
    return all(re.search(rule, password) for rule in rules)

def is_valid_phone(phone):
    return bool(re.fullmatch(r"\d{10}", phone))

def send_email(recipient, subject, body):
    if DEBUG_OTP:
        print(f"[EMAIL DEBUG] To: {recipient}\nSubject: {subject}\n{body}\n")
        return True
    
    sender_email = app.config.get('MAIL_USERNAME', '')
    sender_password = app.config.get('MAIL_PASSWORD', '')
    
    print(f"[EMAIL] Attempting to send email to {recipient}")
    print(f"[EMAIL] Sender: {sender_email}")
    
    if not sender_email or not sender_password:
        print('[EMAIL ERROR] MAIL_USERNAME and MAIL_PASSWORD must be set in .env file')
        return False

    try:
        smtp_server = app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = app.config.get('MAIL_PORT', 587)
        
        print(f"[EMAIL] Connecting to {smtp_server}:{smtp_port}")
        
        # Create message with proper MIME formatting
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        print(f"[EMAIL] Starting SMTP connection...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("[EMAIL] Starting TLS...")
            server.starttls()
            print(f"[EMAIL] Logging in as {sender_email}...")
            server.login(sender_email, sender_password)
            print(f"[EMAIL] Sending email to {recipient}...")
            server.send_message(msg)
            print(f"[EMAIL] ✓ Email sent successfully to {recipient}")

        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email: {e}")
        import traceback
        traceback.print_exc()
        return False

def send_sms_otp(phone_number, otp):
    """Send OTP via SMS using Twilio"""
    try:
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '')
        twilio_number = os.environ.get('TWILIO_PHONE_NUMBER', '')
        
        if not account_sid or not auth_token or not twilio_number:
            print('[SMS ERROR] Twilio credentials not configured in .env')
            return False
        
        print(f"[SMS] Attempting to send OTP to {phone_number}")
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=f"Your Rapid Delivery OTP is: {otp}",
            from_=twilio_number,
            to=phone_number
        )
        
        print(f"[SMS] ✓ OTP sent successfully to {phone_number} (SID: {message.sid})")
        return True
    except Exception as e:
        print(f"[SMS ERROR] Failed to send SMS: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_otp_code(user_input_otp, stored_otp):
    """Verify if user-entered OTP matches stored OTP"""
    return str(user_input_otp).strip() == str(stored_otp).strip()

@app.context_processor
def inject_google_maps_key():
    return {'google_maps_api_key': app.config.get('GOOGLE_MAPS_API_KEY', '')}

@app.template_filter('format_datetime')
def format_datetime(value):
    if not value:
        return '-'
    return value.strftime('%Y-%m-%d %H:%M')

def ensure_shop_scanner_column():
    inspector = inspect(db.engine)
    if 'shop' in inspector.get_table_names():
        columns = [column['name'] for column in inspector.get_columns('shop')]
        if 'scanner_filename' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE shop ADD COLUMN scanner_filename VARCHAR(255)'))
                conn.commit()

        if 'latitude' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE shop ADD COLUMN latitude FLOAT'))
                conn.commit()
        if 'longitude' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE shop ADD COLUMN longitude FLOAT'))
                conn.commit()

def ensure_order_location_columns():
    inspector = inspect(db.engine)
    if 'order' in inspector.get_table_names():
        columns = [column['name'] for column in inspector.get_columns('order')]
        if 'pickup_lat' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE "order" ADD COLUMN pickup_lat FLOAT'))
                conn.commit()
        if 'pickup_lng' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE "order" ADD COLUMN pickup_lng FLOAT'))
                conn.commit()
        if 'delivery_lat' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE "order" ADD COLUMN delivery_lat FLOAT'))
                conn.commit()
        if 'delivery_lng' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE "order" ADD COLUMN delivery_lng FLOAT'))
                conn.commit()

def initialize_database():
    db.create_all()
    ensure_shop_scanner_column()
    ensure_order_location_columns()
    if not User.query.filter_by(email='admin@rapidodelivery.app').first():
        admin = User(
            name='Admin',
            email='admin@rapidodelivery.app',
            role=ROLE_ADMIN,
            address='Head Office',
            phone='0000000000',
            tracking_code=create_tracking_code()
        )
        admin.set_password('Admin123!')
        db.session.add(admin)
        db.session.commit()
    if not Shop.query.first():
        sample_shop = User(
            name='Sample Kitchen',
            email='chef@samplekitchen.com',
            role=ROLE_SHOPKEEPER,
            shop_name='Sample Kitchen',
            address='12 Market Street',
            phone='9998887776',
            tracking_code=create_tracking_code()
        )
        sample_shop.set_password('Chef123!')
        db.session.add(sample_shop)
        db.session.commit()
        shop = Shop(
            owner_id=sample_shop.id,
            name='Sample Kitchen',
            description='Fresh meals ready to order.',
            rating=4.8,
            latitude=28.7041,
            longitude=77.1025
        )
        db.session.add(shop)
        db.session.commit()
        items = [
            Item(shop_id=shop.id, name='Paneer Butter Masala', description='Creamy gravy with soft paneer.', price=220.0, rating=4.7),
            Item(shop_id=shop.id, name='Veg Thali', description='Balanced meal with rice, sabzi and roti.', price=180.0, rating=4.6),
            Item(shop_id=shop.id, name='Masala Dosa', description='Crispy dosa with spicy potato filling.', price=120.0, rating=4.5)
        ]
        db.session.add_all(items)
        db.session.commit()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', '')
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        shop_name = request.form.get('shop_name', '').strip()
        vehicle_number = request.form.get('vehicle_number', '').strip()
        scanner_file = request.files.get('scanner')

        if not name or not is_valid_name(name):
            flash('Name must contain only letters and spaces.', 'danger')
            return redirect(url_for('register'))
        if not email or not is_valid_email(email):
            flash('Please enter a valid email address that includes @ and .', 'danger')
            return redirect(url_for('register'))
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if existing_user.otp and existing_user.otp_expiry and existing_user.otp_expiry > datetime.utcnow():
                session['pending_user_id'] = existing_user.id
                flash('This email is already pending verification. Please verify the OTP or resend it.', 'warning')
                return redirect(url_for('verify_otp'))
            flash('Email already registered. Please log in or use Forgot Password.', 'warning')
            return redirect(url_for('register'))
        if not password or not confirm_password:
            flash('Please enter and confirm your password.', 'danger')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        if not is_valid_password(password):
            flash('Password must be at least 8 characters and include uppercase, lowercase, number, and special character.', 'danger')
            return redirect(url_for('register'))
        if not phone or not is_valid_phone(phone):
            flash('Please enter a valid 10-digit mobile number.', 'danger')
            return redirect(url_for('register'))
        if not address:
            flash('Please enter your address.', 'danger')
            return redirect(url_for('register'))
        if role not in [ROLE_CUSTOMER, ROLE_SHOPKEEPER, ROLE_DELIVERY]:
            flash('Please select a valid role.', 'danger')
            return redirect(url_for('register'))
        if role == ROLE_SHOPKEEPER and not shop_name:
            flash('Please enter your shop name.', 'danger')
            return redirect(url_for('register'))
        if role == ROLE_DELIVERY and not vehicle_number:
            flash('Please enter your vehicle number.', 'danger')
            return redirect(url_for('register'))

        scanner_filename = None
        if role == ROLE_SHOPKEEPER and scanner_file and scanner_file.filename:
            if allowed_file(scanner_file.filename):
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                safe_name = secure_filename(scanner_file.filename)
                scanner_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{safe_name}"
                scanner_file.save(os.path.join(app.config['UPLOAD_FOLDER'], scanner_filename))
            else:
                flash('Scanner upload must be an image (png, jpg, jpeg, gif).', 'warning')
                return redirect(url_for('register'))

        user = User(
            name=name,
            email=email,
            role=role,
            address=address,
            phone=phone,
            shop_name=shop_name if role == ROLE_SHOPKEEPER else None,
            vehicle_number=vehicle_number if role == ROLE_DELIVERY else None,
            tracking_code=create_tracking_code()
        )
        user.set_password(password)
        user.otp = create_otp()
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=15)
        db.session.add(user)
        db.session.commit()

        if role == ROLE_SHOPKEEPER and shop_name:
            shop = Shop(
                owner_id=user.id,
                name=shop_name,
                description='',
                scanner_filename=scanner_filename
            )
            db.session.add(shop)
            db.session.commit()

        send_email(user.email, 'Your OTP for Rapid Delivery Signup', f'Your OTP is {user.otp}. It expires in 15 minutes.')
        session['pending_user_id'] = user.id
        flash('OTP sent to your email. Please verify to complete registration.', 'success')
        return redirect(url_for('verify_otp'))
    return render_template('register.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    user_id = session.get('pending_user_id')
    if not user_id:
        flash('No registration in progress.', 'warning')
        return redirect(url_for('register'))
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        
        if not otp:
            flash('Please enter the OTP code.', 'warning')
            return render_template('verify_otp.html', email=user.email, debug_otp=user.otp if DEBUG_OTP else None)
        
        print(f"[OTP VERIFY] User entered: {otp}, Stored: {user.otp}, Expiry: {user.otp_expiry}")
        
        if not user.otp:
            flash('OTP expired or already used. Please register again.', 'danger')
            session.pop('pending_user_id', None)
            return redirect(url_for('register'))
        
        if user.otp_expiry < datetime.utcnow():
            flash('OTP expired. Please register again.', 'danger')
            session.pop('pending_user_id', None)
            return redirect(url_for('register'))
        
        if verify_otp_code(otp, user.otp):
            user.otp = None
            user.otp_expiry = None
            db.session.commit()
            flash('✅ Email verified! You can now log in.', 'success')
            session.pop('pending_user_id', None)
            return redirect(url_for('login'))
        else:
            flash('❌ Invalid OTP. Please try again.', 'danger')
            print(f"[OTP VERIFY] OTP mismatch!")
    
    return render_template('verify_otp.html', email=user.email, debug_otp=user.otp if DEBUG_OTP else None)

@app.route('/resend-registration-otp')
def resend_registration_otp():
    user_id = session.get('pending_user_id')
    if not user_id:
        flash('No registration in progress.', 'warning')
        return redirect(url_for('register'))
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('register'))

    user.otp = create_otp()
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=15)
    db.session.commit()
    send_email(user.email, 'Your OTP for Rapid Delivery Signup', f'Your OTP is {user.otp}. It expires in 15 minutes.')
    flash('A new OTP has been sent to your email.', 'success')
    return redirect(url_for('verify_otp'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if not email:
            flash('Please enter your email.', 'warning')
            return redirect(url_for('login'))
        if not is_valid_email(email):
            flash('Please enter a valid email address that includes @ and .', 'warning')
            return redirect(url_for('login'))
        if not password:
            flash('Please enter your password.', 'warning')
            return redirect(url_for('login'))
        user = User.query.filter_by(email=email).first()
        if not user or not user.verify_password(password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        flash('Welcome back!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash('Please enter your email.', 'warning')
            return redirect(url_for('forgot_password'))
        if not is_valid_email(email):
            flash('Please enter a valid email address that includes @ and .', 'warning')
            return redirect(url_for('forgot_password'))
        user = User.query.filter_by(email=email).first()
        if user:
            user.otp = create_otp()
            user.otp_expiry = datetime.utcnow() + timedelta(minutes=15)
            db.session.commit()
            send_email(user.email, 'Your OTP to reset password', f'Your reset OTP is {user.otp}.')
            flash('OTP sent to your email.', 'success')
            return redirect(url_for('reset_password', email=user.email))
        flash('Email not found. Please check and try again.', 'warning')
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email', '') or request.form.get('email', '')
    if not email and request.method == 'GET':
        flash('Please enter your email first.', 'warning')
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not email:
            flash('Email is missing.', 'danger')
            return redirect(url_for('forgot_password'))
        if not otp:
            flash('Please enter the reset OTP.', 'warning')
            return redirect(url_for('reset_password', email=email))
        if not password or not confirm_password:
            flash('Please enter and confirm your new password.', 'warning')
            return redirect(url_for('reset_password', email=email))
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('reset_password', email=email))
        if not is_valid_password(password):
            flash('Password must be at least 8 characters and include uppercase, lowercase, number, and special character.', 'danger')
            return redirect(url_for('reset_password', email=email))
        user = User.query.filter_by(email=email).first()
        if user and verify_otp_code(otp, user.otp) and user.otp_expiry > datetime.utcnow():
            user.set_password(password)
            user.otp = None
            user.otp_expiry = None
            db.session.commit()
            flash('Password reset successfully. You can now log in.', 'success')
            return redirect(url_for('login'))
        flash('Invalid OTP or expired code.', 'danger')
    return render_template('reset_password.html', email=email)

@app.route('/track-order/<int:order_id>')
@login_required
def track_order(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.role == ROLE_CUSTOMER and order.customer_id != current_user.id:
        flash('You are not authorized to view this tracking page.', 'danger')
        return redirect(url_for('dashboard'))
    if current_user.role == ROLE_DELIVERY and order.delivery_id != current_user.id:
        flash('You are not authorized to view this tracking page.', 'danger')
        return redirect(url_for('dashboard'))
    if current_user.role == ROLE_SHOPKEEPER and order.shop.owner_id != current_user.id:
        flash('You are not authorized to view this tracking page.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('track_order.html', order=order)

@app.route('/dashboard')
@login_required
def dashboard():
    print(f"Dashboard accessed by user: {current_user.id}, role: {current_user.role}")
    if current_user.role == ROLE_CUSTOMER:
        shops = Shop.query.all()
        orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.created_at.desc()).all()
        return render_template('dashboard_customer.html', shops=shops, orders=orders)
    if current_user.role == ROLE_SHOPKEEPER:
        owned_shops = Shop.query.filter_by(owner_id=current_user.id).all()
        shop = owned_shops[0] if owned_shops else None
        if not shop and current_user.shop_name:
            shop = Shop(owner_id=current_user.id, name=current_user.shop_name, description='')
            db.session.add(shop)
            db.session.commit()
            owned_shops = [shop]
        shop_ids = [s.id for s in owned_shops]
        orders = Order.query.filter(Order.shop_id.in_(shop_ids)).order_by(Order.created_at.desc()).all() if shop_ids else []
        items = shop.items if shop else []
        return render_template('dashboard_shopkeeper.html', shop=shop, orders=orders, items=items)
    if current_user.role == ROLE_DELIVERY:
        orders = Order.query.filter(Order.status.in_(['Accepted', 'On the way'])).order_by(Order.created_at.desc()).all()
        return render_template('dashboard_delivery.html', orders=orders, google_maps_api_key=app.config.get('GOOGLE_MAPS_API_KEY'))
    if current_user.role == ROLE_ADMIN:
        users = User.query.all()
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return render_template('dashboard_admin.html', users=users, orders=orders)
    print(f"Unknown role: {current_user.role}")
    flash('Unknown role. Contact admin.', 'danger')
    return redirect(url_for('logout'))

@app.route('/shop/<int:shop_id>', methods=['GET', 'POST'])
@login_required
def shop_detail(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    if request.method == 'POST' and current_user.role == ROLE_CUSTOMER:
        payment_method = request.form['payment_method']
        delivery_lat = request.form.get('delivery_lat')
        delivery_lng = request.form.get('delivery_lng')
        if not delivery_lat or not delivery_lng:
            flash('Please choose your delivery location on the map.', 'warning')
            return redirect(url_for('shop_detail', shop_id=shop_id))
        try:
            delivery_lat = float(delivery_lat)
            delivery_lng = float(delivery_lng)
        except ValueError:
            flash('Invalid delivery location selected.', 'warning')
            return redirect(url_for('shop_detail', shop_id=shop_id))

        item_ids = request.form.getlist('item_id')
        quantities = request.form.getlist('quantity')
        total = 0
        selected_items = []
        for item_id, qty in zip(item_ids, quantities):
            if not qty or int(qty) <= 0:
                continue
            item = Item.query.get(int(item_id))
            if item:
                quantity = int(qty)
                amount = item.price * quantity
                total += amount
                selected_items.append({
                    'item_id': item.id,
                    'name': item.name,
                    'quantity': quantity,
                    'price': item.price
                })
        if total <= 0:
            flash('Please select at least one item.', 'warning')
            return redirect(url_for('shop_detail', shop_id=shop_id))
        if payment_method == 'UPI':
            session['pending_order'] = {
                'customer_id': current_user.id,
                'shop_id': shop.id,
                'payment_method': 'UPI',
                'items': selected_items,
                'total_amount': total,
                'shop_name': shop.name,
                'delivery_lat': delivery_lat,
                'delivery_lng': delivery_lng,
                'pickup_lat': shop.latitude,
                'pickup_lng': shop.longitude
            }
            return redirect(url_for('online_payment', shop_id=shop.id))
        order = Order(
            customer_id=current_user.id,
            shop_id=shop.id,
            code=create_tracking_code(),
            payment_method=payment_method,
            status='New',
            total_amount=total,
            delivery_lat=delivery_lat,
            delivery_lng=delivery_lng,
            pickup_lat=shop.latitude,
            pickup_lng=shop.longitude
        )
        db.session.add(order)
        db.session.flush()
        for item_data in selected_items:
            db.session.add(OrderItem(order_id=order.id, item_id=item_data['item_id'], quantity=item_data['quantity'], price=item_data['price']))
        db.session.commit()
        flash('Order placed successfully. Use code ' + order.code + ' for tracking.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('shop_detail.html', shop=shop)

@app.route('/api/create-razorpay-order', methods=['POST'])
@login_required
def create_razorpay_order():
    if current_user.role != ROLE_CUSTOMER:
        return jsonify({'error': 'Only customers can create payment orders'}), 403
    
    pending_order = session.get('pending_order')
    if not pending_order:
        return jsonify({'error': 'No pending order found'}), 400
    
    try:
        # Create Razorpay order
        amount = int(pending_order['total_amount'] * 100)  # Amount in paisa
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'order_{current_user.id}_{int(datetime.now().timestamp())}',
            'notes': {
                'customer_id': current_user.id,
                'shop_id': pending_order['shop_id']
            }
        }
        
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        return jsonify({
            'order_id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency'],
            'key': RAZORPAY_KEY_ID
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payment/<int:shop_id>', methods=['GET', 'POST'])
@login_required
def online_payment(shop_id):
    if current_user.role != ROLE_CUSTOMER:
        flash('Only customers can make payments.', 'danger')
        return redirect(url_for('dashboard'))
    pending_order = session.get('pending_order')
    if not pending_order or pending_order.get('shop_id') != shop_id:
        flash('No pending payment found.', 'warning')
        return redirect(url_for('shop_detail', shop_id=shop_id))
    shop = Shop.query.get_or_404(shop_id)
    if request.method == 'POST':
        order = Order(
            customer_id=current_user.id,
            shop_id=shop.id,
            code=create_tracking_code(),
            payment_method=pending_order['payment_method'],
            status='New',
            total_amount=pending_order['total_amount'],
            delivery_lat=pending_order.get('delivery_lat'),
            delivery_lng=pending_order.get('delivery_lng'),
            pickup_lat=pending_order.get('pickup_lat'),
            pickup_lng=pending_order.get('pickup_lng')
        )
        db.session.add(order)
        db.session.flush()
        for item_data in pending_order['items']:
            db.session.add(OrderItem(order_id=order.id, item_id=item_data['item_id'], quantity=item_data['quantity'], price=item_data['price']))
        db.session.commit()
        session.pop('pending_order', None)
        flash('Payment completed and order placed successfully. Use code ' + order.code + ' for tracking.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('payment.html', shop=shop, pending=pending_order)

@app.route('/api/verify-payment', methods=['POST'])
@login_required
def verify_payment():
    if current_user.role != ROLE_CUSTOMER:
        return jsonify({'error': 'Only customers can verify payments'}), 403
    
    data = request.get_json()
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')
    
    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return jsonify({'error': 'Missing payment verification data'}), 400
    
    try:
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Payment verified, now create the order
        pending_order = session.get('pending_order')
        if not pending_order:
            return jsonify({'error': 'No pending order found'}), 400
        
        shop = Shop.query.get_or_404(pending_order['shop_id'])
        
        order = Order(
            customer_id=current_user.id,
            shop_id=shop.id,
            code=create_tracking_code(),
            payment_method='UPI (Razorpay)',
            status='New',
            total_amount=pending_order['total_amount'],
            delivery_lat=pending_order.get('delivery_lat'),
            delivery_lng=pending_order.get('delivery_lng'),
            pickup_lat=pending_order.get('pickup_lat'),
            pickup_lng=pending_order.get('pickup_lng'),
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id
        )
        
        db.session.add(order)
        db.session.flush()
        
        for item_data in pending_order['items']:
            db.session.add(OrderItem(order_id=order.id, item_id=item_data['item_id'], quantity=item_data['quantity'], price=item_data['price']))
        
        db.session.commit()
        session.pop('pending_order', None)
        
        return jsonify({
            'success': True,
            'order_code': order.code,
            'message': 'Payment verified and order placed successfully'
        })
        
    except razorpay.errors.SignatureVerificationError:
        return jsonify({'error': 'Payment verification failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/order/<int:order_id>/accept', methods=['POST'])
@login_required
def accept_order(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.role != ROLE_SHOPKEEPER or order.shop.owner_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    if order.status == 'New':
        order.status = 'Accepted'
        db.session.commit()
        flash('Order accepted. Delivery team can now pick it up.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/order/<int:order_id>/pickup', methods=['POST'])
@login_required
def pickup_order(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.role != ROLE_DELIVERY:
        flash('Only delivery users can accept pickups.', 'danger')
        return redirect(url_for('dashboard'))
    if order.status == 'Accepted':
        order.status = 'On the way'
        order.delivery_id = current_user.id
        order.eta = datetime.utcnow() + timedelta(minutes=18)
        db.session.commit()
        flash('You have picked up the order. Delivery started.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/order/<int:order_id>/deliver', methods=['POST'])
@login_required
def deliver_order(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.role != ROLE_DELIVERY or order.delivery_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    order.status = 'Delivered'
    db.session.commit()
    flash('Order marked as delivered.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add-item', methods=['POST'])
@login_required
def add_item():
    if current_user.role != ROLE_SHOPKEEPER:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('dashboard'))
    shop = Shop.query.filter_by(owner_id=current_user.id).first()
    if not shop:
        flash('No shop found.', 'danger')
        return redirect(url_for('dashboard'))
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    item = Item(shop_id=shop.id, name=name, description=description, price=price)
    db.session.add(item)
    db.session.commit()
    flash('Item added successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/test-email')
@login_required
def test_email():
    if current_user.role != ROLE_ADMIN:
        flash('Admin only.', 'danger')
        return redirect(url_for('dashboard'))
    send_email(current_user.email, 'Test Email', 'This is a test email from Rapid Delivery.')
    flash('Test email sent. Check your inbox.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Location Tracking Routes

@app.route('/api/update-location', methods=['POST'])
@login_required
def update_location():
    """Update delivery person's current location"""
    if current_user.role != ROLE_DELIVERY:
        return jsonify({'success': False, 'error': 'Only delivery persons can update location'}), 403

    data = request.get_json()
    if not data or 'lat' not in data or 'lng' not in data:
        return jsonify({'success': False, 'error': 'Latitude and longitude required'}), 400

    try:
        lat = float(data['lat'])
        lng = float(data['lng'])

        current_user.current_lat = lat
        current_user.current_lng = lng
        current_user.location_updated_at = datetime.utcnow()
        current_user.is_sharing_location = True
        db.session.commit()

        return jsonify({'success': True, 'message': 'Location updated successfully'})
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid coordinates'}), 400

@app.route('/api/stop-location-sharing', methods=['POST'])
@login_required
def stop_location_sharing():
    """Stop sharing location for delivery person"""
    if current_user.role != ROLE_DELIVERY:
        return jsonify({'success': False, 'error': 'Only delivery persons can control location sharing'}), 403

    current_user.is_sharing_location = False
    db.session.commit()

    return jsonify({'success': True, 'message': 'Location sharing stopped'})

@app.route('/api/get-delivery-location/<int:order_id>')
@login_required
def get_delivery_location(order_id):
    """Get current location of delivery person for an order"""
    order = Order.query.get_or_404(order_id)

    # Check if user is authorized to view this order's delivery location
    if (current_user.role == ROLE_CUSTOMER and order.customer_id != current_user.id) or \
       (current_user.role == ROLE_DELIVERY and order.delivery_id != current_user.id) or \
       (current_user.role == ROLE_SHOPKEEPER and order.shop.owner_id != current_user.id):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    if not order.delivery or not order.delivery.is_sharing_location:
        return jsonify({'success': False, 'error': 'Delivery location not available'}), 404

    # Check if location is recent (within last 10 minutes)
    if not order.delivery.location_updated_at or \
       (datetime.utcnow() - order.delivery.location_updated_at).total_seconds() > 600:
        return jsonify({'success': False, 'error': 'Location data is outdated'}), 404

    return jsonify({
        'success': True,
        'location': {
            'lat': order.delivery.current_lat,
            'lng': order.delivery.current_lng,
            'updated_at': order.delivery.location_updated_at.isoformat(),
            'delivery_person': order.delivery.name
        }
    })

@app.route('/api/get-my-location')
@login_required
def get_my_location():
    """Get current delivery person location for dashboard map"""
    if current_user.role != ROLE_DELIVERY:
        return jsonify({'success': False, 'error': 'Only delivery persons can access this endpoint'}), 403

    if not current_user.current_lat or not current_user.current_lng:
        return jsonify({'success': False, 'error': 'Location not available yet'}), 404

    return jsonify({
        'success': True,
        'location': {
            'lat': current_user.current_lat,
            'lng': current_user.current_lng,
            'updated_at': current_user.location_updated_at.isoformat() if current_user.location_updated_at else None,
            'sharing': bool(current_user.is_sharing_location)
        }
    })

@app.route('/api/calculate-eta/<int:order_id>')
@login_required
def calculate_eta(order_id):
    """Calculate ETA from delivery person's current location to customer"""
    order = Order.query.get_or_404(order_id)

    if not order.delivery or not order.delivery.is_sharing_location:
        return jsonify({'success': False, 'error': 'Delivery location not available'}), 404

    if not order.delivery.current_lat or not order.delivery.current_lng:
        return jsonify({'success': False, 'error': 'Delivery location coordinates missing'}), 404

    # Simple distance-based ETA calculation (you can enhance this with Google Maps API)
    # Assuming average speed of 30 km/h in city traffic
    import math

    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371  # Earth's radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    distance = haversine_distance(
        order.delivery.current_lat, order.delivery.current_lng,
        order.delivery_lat, order.delivery_lng
    )

    # Average speed: 30 km/h = 0.5 km/min
    eta_minutes = int(distance / 0.5)

    # Add buffer time for traffic/loading
    eta_minutes = max(eta_minutes + 5, 1)

    return jsonify({
        'success': True,
        'eta_minutes': eta_minutes,
        'distance_km': round(distance, 2),
        'current_location': {
            'lat': order.delivery.current_lat,
            'lng': order.delivery.current_lng
        },
        'destination': {
            'lat': order.delivery_lat,
            'lng': order.delivery_lng
        }
    })

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for a food delivery platform. Help users with order tracking, recommendations, and support."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150
        )
        ai_reply = response.choices[0].message.content.strip()
        
        # Store conversation in MongoDB
        chat_collection = mongo_db['chats']
        chat_collection.insert_one({
            'user_id': current_user.id,
            'user_message': user_message,
            'ai_reply': ai_reply,
            'timestamp': datetime.utcnow()
        })
        
        return jsonify({'reply': ai_reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/history', methods=['GET'])
@login_required
def chat_history():
    chat_collection = mongo_db['chats']
    chats = list(chat_collection.find({'user_id': current_user.id}).sort('timestamp', -1).limit(10))
    for chat in chats:
        chat['_id'] = str(chat['_id'])  # Convert ObjectId to string
    return jsonify({'history': chats})

if __name__ == '__main__':
    with app.app_context():
        initialize_database()
    app.run(debug=True)
