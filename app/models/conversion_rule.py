"""ConversionRule Model — 轉換規則資料表"""

from datetime import datetime
from . import db


class ConversionRule(db.Model):
    """轉換規則模型

    儲存各運動類型的步數轉換公式與強度調整係數。
    轉換引擎根據此表的規則進行步數計算。
    """
    __tablename__ = 'conversion_rule'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exercise_type = db.Column(db.String(30), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    base_steps_per_unit = db.Column(db.Float, nullable=False)
    low_intensity_factor = db.Column(db.Float, nullable=False, default=0.8)
    medium_intensity_factor = db.Column(db.Float, nullable=False, default=1.0)
    high_intensity_factor = db.Column(db.Float, nullable=False, default=1.3)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_intensity_factor(self, intensity):
        """根據強度等級回傳對應的調整係數

        Args:
            intensity: 'low' / 'medium' / 'high'

        Returns:
            float: 強度調整係數
        """
        factors = {
            'low': self.low_intensity_factor,
            'medium': self.medium_intensity_factor,
            'high': self.high_intensity_factor
        }
        return factors.get(intensity, self.medium_intensity_factor)

    # ── CRUD 方法 ──

    @classmethod
    def create(cls, exercise_type, display_name, unit, base_steps_per_unit,
               low_intensity_factor=0.8, medium_intensity_factor=1.0,
               high_intensity_factor=1.3, description=None):
        """建立新轉換規則"""
        rule = cls(
            exercise_type=exercise_type,
            display_name=display_name,
            unit=unit,
            base_steps_per_unit=base_steps_per_unit,
            low_intensity_factor=low_intensity_factor,
            medium_intensity_factor=medium_intensity_factor,
            high_intensity_factor=high_intensity_factor,
            description=description
        )
        db.session.add(rule)
        db.session.commit()
        return rule

    @classmethod
    def get_all(cls):
        """取得所有轉換規則"""
        return cls.query.all()

    @classmethod
    def get_active_rules(cls):
        """取得所有啟用中的轉換規則"""
        return cls.query.filter_by(is_active=True).all()

    @classmethod
    def get_by_id(cls, rule_id):
        """依 ID 取得轉換規則"""
        return cls.query.get(rule_id)

    @classmethod
    def get_by_type(cls, exercise_type):
        """依運動類型取得轉換規則"""
        return cls.query.filter_by(exercise_type=exercise_type, is_active=True).first()

    def update(self, **kwargs):
        """更新轉換規則"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ('id', 'created_at'):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self

    def delete(self):
        """刪除轉換規則"""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def seed_default_rules(cls):
        """初始化預設轉換規則（種子資料）

        僅在資料表為空時執行插入。
        """
        if cls.query.count() > 0:
            return

        default_rules = [
            ('freestyle',    '自由式游泳', 'minutes', 120.0, 0.8, 1.0, 1.3, '自由式每分鐘轉換基準 120 步'),
            ('breaststroke', '蛙式游泳',   'minutes', 100.0, 0.8, 1.0, 1.3, '蛙式每分鐘轉換基準 100 步'),
            ('backstroke',   '仰式游泳',   'minutes',  90.0, 0.8, 1.0, 1.3, '仰式每分鐘轉換基準 90 步'),
            ('butterfly',    '蝶式游泳',   'minutes', 150.0, 0.8, 1.0, 1.3, '蝶式每分鐘轉換基準 150 步'),
            ('rowing',       '划船',       'minutes',  80.0, 0.8, 1.0, 1.3, '划船每分鐘轉換基準 80 步'),
            ('stroke_count', '划水次數',   'strokes',   2.0, 1.0, 1.0, 1.0, '每次划水轉換 2 步（不受強度影響）'),
            ('distance',     '游泳距離',   'meters',    2.0, 1.0, 1.0, 1.0, '每公尺轉換 2 步（100 公尺 = 200 步）'),
        ]

        for rule_data in default_rules:
            rule = cls(
                exercise_type=rule_data[0],
                display_name=rule_data[1],
                unit=rule_data[2],
                base_steps_per_unit=rule_data[3],
                low_intensity_factor=rule_data[4],
                medium_intensity_factor=rule_data[5],
                high_intensity_factor=rule_data[6],
                description=rule_data[7]
            )
            db.session.add(rule)

        db.session.commit()

    def __repr__(self):
        return f'<ConversionRule {self.id}: {self.display_name} ({self.base_steps_per_unit} steps/{self.unit})>'
