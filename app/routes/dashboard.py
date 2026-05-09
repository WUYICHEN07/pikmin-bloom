"""進度看板路由 — 步數統計與圖表數據"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('', methods=['GET'])
@login_required
def index():
    """顯示進度追蹤看板首頁

    處理：
      1. Conversion.get_today_steps(user_id) → 今日累計步數
      2. Conversion.get_weekly_steps(user_id) → 本週累計步數
      3. Conversion.get_monthly_steps(user_id) → 本月累計步數
      4. Conversion.get_total_steps(user_id) → 累計總步數
      5. Conversion.get_daily_summary(user_id, 30) → 近 30 天每日數據（圖表用）
    輸出：渲染 dashboard/index.html，傳入統計數據與圖表資料
    """
    pass
