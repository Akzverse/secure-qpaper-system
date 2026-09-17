from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
import os
import io
import uuid
from dotenv import load_dotenv
import pyaes

load_dotenv()

app = Flask(__name__)
database_url = os.getenv('DATABASE_URL', 'sqlite:///qpaper_system.db')
# Some cloud dashboards provide the older postgres:// scheme. SQLAlchemy needs
# the explicit PostgreSQL driver name used by this project.
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
elif database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'local-development-only-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB upload limit
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db = SQLAlchemy(app)

# ============= DATABASE MODELS =============

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # question_setter, reviewer, admin, exam_officer
    mfa_secret = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)

class QuestionPaper(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    encrypted_content = db.Column(db.LargeBinary, nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    exam_date = db.Column(db.DateTime, nullable=False)
    is_released = db.Column(db.Boolean, default=False)
    released_at = db.Column(db.DateTime)
    encryption_key = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, approved, released

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.String(100))
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ip_address = db.Column(db.String(45))
    status = db.Column(db.String(20), default='success')  # success, failure, unauthorized

class RolePermission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)
    permission = db.Column(db.String(100), nullable=False)

# ============= UTILITY FUNCTIONS =============

def get_encryption_key():
    """Return a 32-byte AES-256 key stored outside the database.

    A cloud deployment must set ENCRYPTION_KEY as an environment variable. A local
    development key is generated once in encryption.key, which is git-ignored.
    """
    configured_key = os.getenv('ENCRYPTION_KEY')
    if configured_key:
        try:
            key = base64.urlsafe_b64decode(configured_key.encode('utf-8'))
        except Exception as exc:
            raise ValueError('ENCRYPTION_KEY must be Base64-encoded.') from exc
        if len(key) != 32:
            raise ValueError('ENCRYPTION_KEY must decode to exactly 32 bytes.')
        return key

    key_file = 'encryption.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            key = f.read()
        if len(key) == 32:
            return key

    key = os.urandom(32)
    with open(key_file, 'wb') as f:
        f.write(key)
    return key

def encrypt_file(file_content, key):
    """AES-256-CTR encrypt, then authenticate encrypted data with HMAC-SHA-256."""
    iv = os.urandom(16)
    counter = pyaes.Counter(initial_value=int.from_bytes(iv, byteorder='big'))
    ciphertext = pyaes.AESModeOfOperationCTR(key, counter=counter).encrypt(file_content)
    tag = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()
    return b'QP1' + iv + tag + ciphertext

def decrypt_file(encrypted_content, key):
    """Verify HMAC before decrypting the AES-256 protected question paper."""
    if len(encrypted_content) < 51 or encrypted_content[:3] != b'QP1':
        raise ValueError('Invalid encrypted file format.')
    iv, tag, ciphertext = encrypted_content[3:19], encrypted_content[19:51], encrypted_content[51:]
    expected_tag = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected_tag):
        raise ValueError('Encrypted file integrity check failed.')
    counter = pyaes.Counter(initial_value=int.from_bytes(iv, byteorder='big'))
    return pyaes.AESModeOfOperationCTR(key, counter=counter).decrypt(ciphertext)

def generate_file_hash(file_content):
    """Generate SHA-256 hash of file"""
    return hashlib.sha256(file_content).hexdigest()

def log_action(user_id, action, resource_type, resource_id=None, details=None, status='success'):
    """Log all user actions"""
    try:
        # Skip audit log if user_id is None (e.g., failed login attempt)
        if user_id is None:
            return
        
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr,
            status=status
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        print(f"Audit log error: {e}")

def init_permissions():
    """Initialize role-based permissions"""
    permissions = {
        'question_setter': ['create_qpaper', 'edit_own_qpaper', 'view_own_qpaper'],
        'reviewer': ['view_qpaper', 'approve_qpaper', 'reject_qpaper'],
        'admin': ['view_all_qpapers', 'manage_users', 'view_logs', 'system_config'],
        'exam_officer': ['view_approved_qpapers', 'release_qpaper', 'distribute_qpaper']
    }
    
    for role, perms in permissions.items():
        for perm in perms:
            if not RolePermission.query.filter_by(role=role, permission=perm).first():
                db.session.add(RolePermission(role=role, permission=perm))
    db.session.commit()

# ============= AUTHENTICATION & AUTHORIZATION =============

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            log_action(None, 'unauthorized_access', 'auth', status='failure')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_active:
            session.clear()
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user = User.query.get(session['user_id'])
            if user.role not in roles:
                log_action(user.id, 'unauthorized_role_access', 'auth', status='failure')
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============= ROUTES =============

@app.before_request
def before_request():
    session.permanent = True

@app.route('/health', methods=['GET'])
def health():
    """Small health endpoint used by a cloud host to confirm the app is alive."""
    return jsonify({
        'status': 'ok',
        'database': 'cloud-postgresql' if database_url.startswith('postgresql+') else 'local-sqlite'
    })

@app.route('/', methods=['GET'])
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # Privileged roles must be provisioned by an administrator, not selected
        # by a visitor on the public registration page.
        role = 'question_setter'
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already exists')
        
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        
        log_action(user.id, 'user_registration', 'user', user.id)
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        mfa_code = request.form.get('mfa_code', '')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            log_action(None, 'failed_login', 'auth', details=f'username: {username}', status='failure')
            return render_template('login.html', error='Invalid credentials')
        
        if not user.is_active:
            log_action(user.id, 'inactive_user_login', 'auth', status='failure')
            return render_template('login.html', error='User account is inactive')
        
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        log_action(user.id, 'user_login', 'auth')
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    user_id = session.get('user_id')
    if user_id:
        log_action(user_id, 'user_logout', 'auth')
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET'])
@require_login
def dashboard():
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if user.role == 'question_setter':
        qpapers = QuestionPaper.query.filter_by(created_by=user_id).all()
    elif user.role == 'admin':
        qpapers = QuestionPaper.query.all()
    elif user.role == 'exam_officer':
        qpapers = QuestionPaper.query.filter_by(status='approved').all()
    else:
        qpapers = QuestionPaper.query.all()
    
    return render_template('dashboard.html', user=user, qpapers=qpapers, now=datetime.now)

@app.route('/upload', methods=['GET', 'POST'])
@require_login
@require_role('question_setter')
def upload_qpaper():
    if request.method == 'POST':
        title = request.form.get('title')
        subject = request.form.get('subject')
        exam_date = request.form.get('exam_date')
        file = request.files.get('file')
        
        if not all([title, subject, exam_date, file]):
            return render_template('upload.html', error='All fields are required')
        
        try:
            file_content = file.read()
            allowed_extensions = {'pdf', 'doc', 'docx'}
            extension = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            if not file_content or extension not in allowed_extensions:
                return render_template('upload.html', error='Upload a non-empty PDF, DOC, or DOCX file.')
            
            encryption_key = get_encryption_key()
            encrypted_content = encrypt_file(file_content, encryption_key)
            file_hash = generate_file_hash(file_content)
            
            qpaper = QuestionPaper(
                title=title,
                subject=subject,
                encrypted_content=encrypted_content,
                file_hash=file_hash,
                created_by=session['user_id'],
                exam_date=datetime.fromisoformat(exam_date),
                # The actual key is held in an environment variable (cloud) or
                # the git-ignored local key file, never inside the database.
                encryption_key='environment-managed'
            )
            db.session.add(qpaper)
            db.session.commit()
            
            log_action(session['user_id'], 'qpaper_upload', 'question_paper', qpaper.id)
            return redirect(url_for('dashboard'))
        except Exception as e:
            print(f"Upload error: {e}")
            return render_template('upload.html', error=f'Upload failed: {str(e)}')
    
    return render_template('upload.html')

@app.route('/qpaper/<qpaper_id>/view', methods=['GET'])
@require_login
def view_qpaper(qpaper_id):
    qpaper = QuestionPaper.query.get(qpaper_id)
    
    if not qpaper:
        return jsonify({'error': 'Question paper not found'}), 404
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Role-based access control
    if user.role == 'question_setter' and qpaper.created_by != user_id:
        log_action(user_id, 'unauthorized_qpaper_view', 'question_paper', qpaper_id, status='failure')
        return jsonify({'error': 'Access denied'}), 403
    
    if user.role == 'exam_officer' and qpaper.status != 'approved':
        log_action(user_id, 'unauthorized_qpaper_view', 'question_paper', qpaper_id, status='failure')
        return jsonify({'error': 'Question paper not yet approved for release'}), 403
    
    # Check time-based release
    if not qpaper.is_released and qpaper.exam_date > datetime.now():
        log_action(user_id, 'premature_qpaper_access_attempt', 'question_paper', qpaper_id, status='failure')
        return jsonify({'error': 'Question paper cannot be accessed before exam date'}), 403
    
    try:
        encryption_key = get_encryption_key()
        decrypted_content = decrypt_file(qpaper.encrypted_content, encryption_key)
        
        # Verify integrity
        current_hash = generate_file_hash(decrypted_content)
        if current_hash != qpaper.file_hash:
            log_action(user_id, 'integrity_check_failed', 'question_paper', qpaper_id, status='failure')
            return jsonify({'error': 'Integrity verification failed - file may have been tampered'}), 403
        
        log_action(user_id, 'qpaper_view', 'question_paper', qpaper_id)
        
        return send_file(
            io.BytesIO(decrypted_content),
            as_attachment=True,
            download_name=f"{qpaper.title}.pdf"
        )
    except Exception as e:
        log_action(user_id, 'qpaper_view_failed', 'question_paper', qpaper_id, status='failure')
        return jsonify({'error': f'Decryption failed: {str(e)}'}), 500

@app.route('/qpaper/<qpaper_id>/approve', methods=['POST'])
@require_login
@require_role('reviewer')
def approve_qpaper(qpaper_id):
    qpaper = QuestionPaper.query.get(qpaper_id)
    
    if not qpaper:
        return jsonify({'error': 'Question paper not found'}), 404
    
    qpaper.status = 'approved'
    db.session.commit()
    
    log_action(session['user_id'], 'qpaper_approved', 'question_paper', qpaper_id)
    return jsonify({'message': 'Question paper approved'}), 200

@app.route('/qpaper/<qpaper_id>/release', methods=['POST'])
@require_login
@require_role('exam_officer')
def release_qpaper(qpaper_id):
    qpaper = QuestionPaper.query.get(qpaper_id)
    
    if not qpaper:
        return jsonify({'error': 'Question paper not found'}), 404
    
    if qpaper.status != 'approved':
        return jsonify({'error': 'Question paper must be approved before release'}), 403

    if qpaper.exam_date > datetime.now():
        log_action(session['user_id'], 'premature_release_attempt', 'question_paper', qpaper_id, status='failure')
        return jsonify({'error': 'Question paper cannot be released before the scheduled exam date'}), 403
    
    qpaper.is_released = True
    qpaper.released_at = datetime.utcnow()
    db.session.commit()
    
    log_action(session['user_id'], 'qpaper_released', 'question_paper', qpaper_id)
    return jsonify({'message': 'Question paper released'}), 200

@app.route('/audit-logs', methods=['GET'])
@require_login
@require_role('admin')
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    
    logs_data = []
    for log in logs:
        user = User.query.get(log.user_id)
        logs_data.append({
            'timestamp': log.timestamp.isoformat(),
            'username': user.username if user else 'System',
            'action': log.action,
            'resource': f"{log.resource_type}:{log.resource_id}",
            'status': log.status,
            'ip': log.ip_address
        })
    
    return render_template('audit_logs.html', logs=logs_data)

@app.route('/admin/users', methods=['GET'])
@require_login
@require_role('admin')
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)

# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# ============= DATABASE INITIALIZATION =============

def init_db():
    with app.app_context():
        db.create_all()
        init_permissions()
        
        # Create default admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@qpaper.local',
                password=generate_password_hash('admin@123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username=admin, password=admin@123")

init_db()

if __name__ == '__main__':
    app.run(
        debug=os.getenv('DEBUG', 'False').lower() == 'true',
        host=os.getenv('APP_HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', os.getenv('APP_PORT', '5000')))
    )
