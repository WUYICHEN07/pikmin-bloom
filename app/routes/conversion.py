"""步數轉換路由 — 快速轉換、轉換結果"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

bp = Blueprint('conversion', __name__, url_prefix='/conversion')


@bp.route('/quick', methods=['GET'])
@login_required
def quick_page():
    """顯示一鍵快速轉換頁面

    預填上次使用的運動設定，渲染 conversion/quick.html。
    """
    pass


@bp.route('/quick', methods=['POST'])
@login_required
def quick_convert():
    """執行一鍵快速轉換

    驗證 → 儲存 → 轉換 → 重導向結果頁。
    """
    pass


@bp.route('/result/<int:id>', methods=['GET'])
@login_required
def result(id):
    """顯示轉換結果頁面

    查詢轉換紀錄，渲染 conversion/result.html（含動畫）。
    錯誤：紀錄不存在 → 404；非本人紀錄 → 403。
    """
    pass
