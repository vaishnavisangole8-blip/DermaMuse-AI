"""
Module 1 – User Authentication
Handles registration, login, logout using bcrypt password hashing.
"""
import re
import bcrypt
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash)
from database.db import query

auth_bp = Blueprint('auth', __name__)

# ── Helpers ───────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def check_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def is_valid_email(email: str) -> bool:
    return bool(re.match(r'^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$', email, re.I))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name      = request.form.get('name', '').strip()
        email     = request.form.get('email', '').strip().lower()
        password  = request.form.get('password', '')
        confirm   = request.form.get('confirm_password', '')
        age_group = request.form.get('age_group', '18-24')

        # Validation
        if not all([name, email, password, confirm]):
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        if not is_valid_email(email):
            flash('Invalid email address.', 'danger')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        # Duplicate check
        existing = query('SELECT user_id FROM users WHERE email=%s',
                         (email,), fetchone=True)
        if existing:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('auth.login'))

        hashed = hash_password(password)
        uid = query(
            'INSERT INTO users (name, email, password, age_group) VALUES (%s,%s,%s,%s)',
            (name, email, hashed, age_group), commit=True
        )
        session.permanent = True
        session['user_id']   = uid
        session['user_name'] = name
        flash(f'Welcome, {name}! Account created successfully.', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')

        user = query('SELECT * FROM users WHERE email=%s', (email,), fetchone=True)
        if not user or not check_password(password, user['password']):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')

        session.permanent = True
        session['user_id']   = user['user_id']
        session['user_name'] = user['name']
        flash(f'Welcome back, {user["name"]}!', 'success')
        return redirect(url_for('main.index'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
