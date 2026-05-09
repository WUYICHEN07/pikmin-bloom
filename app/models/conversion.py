"""Conversion Model — 步數轉換紀錄資料表"""

from datetime import datetime, timedelta
from sqlalchemy import func
from . import db


class Conversion(db.Model):
    """步數轉換紀錄模型

    儲存每次運動數據經轉換引擎計算後的步數結果，
    包含使用的轉換率與計算過程。
    """
    __tablename__ = 'conversion'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id', ondelete='CASCADE'), nullable=False, index=True)
    conversion_rule_id = db.Column(db.Integer, db.ForeignKey('conversion_rule.id'), nullable=False)
    converted_steps = db.Column(db.Integer, nullable=False)
    conversion_rate = db.Column(db.Float, nullable=False)
    calculation_detail = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    # 關聯
    rule = db.relationship('ConversionRule', backref='conversions')

    # ── CRUD 方法 ──

    @classmethod
    def create(cls, user_id, exercise_id, conversion_rule_id,
               converted_steps, conversion_rate, calculation_detail=None):
        """建立新轉換紀錄"""
        conversion = cls(
            user_id=user_id,
            exercise_id=exercise_id,
            conversion_rule_id=conversion_rule_id,
            converted_steps=converted_steps,
            conversion_rate=conversion_rate,
            calculation_detail=calculation_detail
        )
        db.session.add(conversion)
        db.session.commit()
        return conversion

    @classmethod
    def get_all(cls):
        """取得所有轉換紀錄"""
        return cls.query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_id(cls, conversion_id):
        """依 ID 取得轉換紀錄"""
        return cls.query.get(conversion_id)

    @classmethod
    def get_by_user_id(cls, user_id):
        """取得指定使用者的所有轉換紀錄"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_today_steps(cls, user_id):
        """取得指定使用者今日累計步數"""
        today = datetime.utcnow().date()
        result = db.session.query(func.sum(cls.converted_steps)).filter(
            cls.user_id == user_id,
            func.date(cls.created_at) == today
        ).scalar()
        return result or 0

    @classmethod
    def get_weekly_steps(cls, user_id):
        """取得指定使用者本週累計步數"""
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        result = db.session.query(func.sum(cls.converted_steps)).filter(
            cls.user_id == user_id,
            func.date(cls.created_at) >= week_start
        ).scalar()
        return result or 0

    @classmethod
    def get_monthly_steps(cls, user_id):
        """取得指定使用者本月累計步數"""
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
        result = db.session.query(func.sum(cls.converted_steps)).filter(
            cls.user_id == user_id,
            func.date(cls.created_at) >= month_start
        ).scalar()
        return result or 0

    @classmethod
    def get_total_steps(cls, user_id):
        """取得指定使用者累計總步數"""
        result = db.session.query(func.sum(cls.converted_steps)).filter(
            cls.user_id == user_id
        ).scalar()
        return result or 0

    @classmethod
    def get_daily_summary(cls, user_id, days=30):
        """取得指定使用者每日步數摘要（圖表用）"""
        since = datetime.utcnow().date() - timedelta(days=days)
        results = db.session.query(
            func.date(cls.created_at).label('date'),
            func.sum(cls.converted_steps).label('total_steps')
        ).filter(
            cls.user_id == user_id,
            func.date(cls.created_at) >= since
        ).group_by(
            func.date(cls.created_at)
        ).order_by(
            func.date(cls.created_at)
        ).all()
        return [{'date': str(r.date), 'steps': r.total_steps} for r in results]

    def update(self, **kwargs):
        """更新轉換紀錄"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ('id', 'user_id', 'exercise_id', 'created_at'):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除轉換紀錄"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<Conversion {self.id}: {self.converted_steps} steps>'
