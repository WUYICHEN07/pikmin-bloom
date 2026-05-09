-- ============================================================
-- 皮克敏水性類型運動換算步數系統 — SQLite 建表語法
-- 建立日期：2026-05-09
-- ============================================================

-- 啟用外鍵約束
PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- 1. USER（使用者）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    email               VARCHAR(120) NOT NULL UNIQUE,
    password_hash       VARCHAR(255) NOT NULL,
    nickname            VARCHAR(50)  NOT NULL,
    preferred_sport     VARCHAR(30)  DEFAULT 'freestyle',
    preferred_theme     VARCHAR(20)  DEFAULT 'ocean',
    last_exercise_type  VARCHAR(30)  DEFAULT NULL,
    last_intensity      VARCHAR(10)  DEFAULT NULL,
    created_at          DATETIME     NOT NULL DEFAULT (datetime('now')),
    updated_at          DATETIME     NOT NULL DEFAULT (datetime('now'))
);

-- ------------------------------------------------------------
-- 2. EXERCISE（運動紀錄）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS exercise (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER      NOT NULL,
    exercise_type     VARCHAR(30)  NOT NULL,
    intensity         VARCHAR(10)  NOT NULL DEFAULT 'medium',
    duration_minutes  FLOAT        DEFAULT NULL,
    stroke_count      INTEGER      DEFAULT NULL,
    distance_meters   FLOAT        DEFAULT NULL,
    raw_data          TEXT         DEFAULT NULL,
    exercise_date     DATETIME     NOT NULL DEFAULT (datetime('now')),
    created_at        DATETIME     NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_exercise_user_id ON exercise(user_id);
CREATE INDEX IF NOT EXISTS idx_exercise_date ON exercise(exercise_date);

-- ------------------------------------------------------------
-- 3. CONVERSION_RULE（轉換規則）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversion_rule (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_type             VARCHAR(30)  NOT NULL UNIQUE,
    display_name              VARCHAR(50)  NOT NULL,
    unit                      VARCHAR(20)  NOT NULL,
    base_steps_per_unit       FLOAT        NOT NULL,
    low_intensity_factor      FLOAT        NOT NULL DEFAULT 0.8,
    medium_intensity_factor   FLOAT        NOT NULL DEFAULT 1.0,
    high_intensity_factor     FLOAT        NOT NULL DEFAULT 1.3,
    description               TEXT         DEFAULT NULL,
    is_active                 BOOLEAN      NOT NULL DEFAULT 1,
    created_at                DATETIME     NOT NULL DEFAULT (datetime('now')),
    updated_at                DATETIME     NOT NULL DEFAULT (datetime('now'))
);

-- ------------------------------------------------------------
-- 4. CONVERSION（步數轉換紀錄）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversion (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    exercise_id         INTEGER NOT NULL,
    conversion_rule_id  INTEGER NOT NULL,
    converted_steps     INTEGER NOT NULL,
    conversion_rate     FLOAT   NOT NULL,
    calculation_detail  TEXT    DEFAULT NULL,
    created_at          DATETIME NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id)            REFERENCES user(id)            ON DELETE CASCADE,
    FOREIGN KEY (exercise_id)        REFERENCES exercise(id)        ON DELETE CASCADE,
    FOREIGN KEY (conversion_rule_id) REFERENCES conversion_rule(id)
);

CREATE INDEX IF NOT EXISTS idx_conversion_user_id ON conversion(user_id);
CREATE INDEX IF NOT EXISTS idx_conversion_exercise_id ON conversion(exercise_id);
CREATE INDEX IF NOT EXISTS idx_conversion_created_at ON conversion(created_at);

-- ============================================================
-- 預設轉換規則（種子資料）
-- ============================================================
INSERT INTO conversion_rule (exercise_type, display_name, unit, base_steps_per_unit, low_intensity_factor, medium_intensity_factor, high_intensity_factor, description)
VALUES
    ('freestyle',    '自由式游泳', 'minutes', 120.0, 0.8, 1.0, 1.3, '自由式每分鐘轉換基準 120 步'),
    ('breaststroke', '蛙式游泳',   'minutes', 100.0, 0.8, 1.0, 1.3, '蛙式每分鐘轉換基準 100 步'),
    ('backstroke',   '仰式游泳',   'minutes',  90.0, 0.8, 1.0, 1.3, '仰式每分鐘轉換基準 90 步'),
    ('butterfly',    '蝶式游泳',   'minutes', 150.0, 0.8, 1.0, 1.3, '蝶式每分鐘轉換基準 150 步'),
    ('rowing',       '划船',       'minutes',  80.0, 0.8, 1.0, 1.3, '划船每分鐘轉換基準 80 步'),
    ('stroke_count', '划水次數',   'strokes',   2.0, 1.0, 1.0, 1.0, '每次划水轉換 2 步（不受強度影響）'),
    ('distance',     '游泳距離',   'meters',    2.0, 1.0, 1.0, 1.0, '每 100 公尺轉換 200 步（基準為每公尺 2 步）');
