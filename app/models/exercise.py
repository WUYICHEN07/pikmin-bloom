"""Exercise Model — 運動紀錄資料表"""

from datetime import datetime
from . import db


class Exercise(db.Model):
    """運動紀錄模型

    儲存使用者上傳的原始運動數據，包含運動類型、時間、
    划水次數、距離等資訊。
    """
    __tablename__ = 'exercise'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    exercise_type = db.Column(db.String(30), nullable=False)
    intensity = db.Column(db.String(10), nullable=False, default='medium')
    duration_minutes = db.Column(db.Float, nullable=True)
    stroke_count = db.Column(db.Integer, nullable=True)
    distance_meters = db.Column(db.Float, nullable=True)
    raw_data = db.Column(db.Text, nullable=True)
    exercise_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯
    conversion = db.relationship('Conversion', backref='exercise', uselist=False, cascade='all, delete-orphan')

    # ── CRUD 方法 ──

    @classmethod
    def create(cls, user_id, exercise_type, intensity='medium',
               duration_minutes=None, stroke_count=None, distance_meters=None,
               raw_data=None, exercise_date=None):
        """建立新運動紀錄"""
        exercise = cls(
            user_id=user_id,
            exercise_type=exercise_type,
            intensity=intensity,
            duration_minutes=duration_minutes,
            stroke_count=stroke_count,
            distance_meters=distance_meters,
            raw_data=raw_data,
            exercise_date=exercise_date or datetime.utcnow()
        )
        db.session.add(exercise)
        db.session.commit()
        return exercise

    @classmethod
    def get_all(cls):
        """取得所有運動紀錄"""
        return cls.query.order_by(cls.exercise_date.desc()).all()

    @classmethod
    def get_by_id(cls, exercise_id):
        """依 ID 取得運動紀錄"""
        return cls.query.get(exercise_id)

    @classmethod
    def get_by_user_id(cls, user_id):
        """取得指定使用者的所有運動紀錄"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.exercise_date.desc()).all()

    @classmethod
    def get_by_user_and_date_range(cls, user_id, start_date, end_date):
        """取得指定使用者在日期範圍內的運動紀錄"""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.exercise_date >= start_date,
            cls.exercise_date <= end_date
        ).order_by(cls.exercise_date.desc()).all()

    def update(self, **kwargs):
        """更新運動紀錄"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ('id', 'user_id', 'created_at'):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除運動紀錄（含關聯的轉換紀錄）"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<Exercise {self.id}: {self.exercise_type} by User {self.user_id}>'
