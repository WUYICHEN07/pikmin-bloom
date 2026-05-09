"""User Model — 使用者資料表"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager


class User(UserMixin, db.Model):
    """使用者模型

    儲存帳號資訊與個人偏好設定。
    繼承 UserMixin 以支援 Flask-Login 的使用者管理功能。
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    preferred_sport = db.Column(db.String(30), default='freestyle')
    preferred_theme = db.Column(db.String(20), default='ocean')
    last_exercise_type = db.Column(db.String(30), nullable=True)
    last_intensity = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    exercises = db.relationship('Exercise', backref='user', lazy=True, cascade='all, delete-orphan')
    conversions = db.relationship('Conversion', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """使用 bcrypt 加密密碼"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """驗證密碼"""
        return check_password_hash(self.password_hash, password)

    # ── CRUD 方法 ──

    @classmethod
    def create(cls, email, password, nickname, preferred_sport='freestyle', preferred_theme='ocean'):
        """建立新使用者"""
        user = cls(email=email, nickname=nickname,
                   preferred_sport=preferred_sport, preferred_theme=preferred_theme)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_all(cls):
        """取得所有使用者"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, user_id):
        """依 ID 取得使用者"""
        return cls.query.get(user_id)

    @classmethod
    def get_by_email(cls, email):
        """依 Email 取得使用者"""
        return cls.query.filter_by(email=email).first()

    def update(self, **kwargs):
        """更新使用者資料"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ('id', 'password_hash', 'created_at'):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self

    def delete(self):
        """刪除使用者"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<User {self.id}: {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login 回呼：根據 Session 中的 user_id 載入使用者"""
    return User.query.get(int(user_id))
