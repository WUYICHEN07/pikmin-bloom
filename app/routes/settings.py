"""個人設定路由 — 資料更新、主題切換、數據匯出"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user

bp = Blueprint('settings', __name__, url_prefix='/settings')


@bp.route('', methods=['GET'])
@login_required
def index():
    """顯示設定頁面

    渲染 settings/index.html，傳入使用者資料與可用主題列表。
    """
    pass


@bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    """更新個人資料

    輸入：表單欄位 nickname、preferred_sport
    處理：current_user.update(...)
    輸出：重導向 /settings，Flash「資料已更新」
    """
    pass


@bp.route('/theme', methods=['POST'])
@login_required
def update_theme():
    """切換背景主題

    輸入：表單欄位 theme（ocean / lake / pool / river）
    處理：current_user.update(preferred_theme=theme)
    輸出：重導向 /settings，Flash「主題已切換」
    """
    pass


@bp.route('/export', methods=['GET'])
@login_required
def export_data():
    """匯出運動數據為 CSV

    處理：查詢使用者所有紀錄，產生 CSV 內容
    輸出：回傳 CSV 檔案下載（Content-Disposition: attachment）
    錯誤：無紀錄 → Flash「尚無可匯出的紀錄」
    """
    pass
