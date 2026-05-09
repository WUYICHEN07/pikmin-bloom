"""認證路由 — 登入、註冊、登出"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET'])
def login_page():
    """顯示登入頁面

    - 若使用者已登入，重導向至 /dashboard
    - 渲染 auth/login.html
    """
    pass


@bp.route('/login', methods=['POST'])
def login():
    """處理登入驗證

    輸入：表單欄位 email、password
    處理：
      1. User.get_by_email(email) 查詢使用者
      2. user.check_password(password) 驗證密碼
      3. 成功 → login_user(user)，重導向 /dashboard
      4. 失敗 → Flash 錯誤訊息，重新渲染登入頁
    """
    pass


@bp.route('/register', methods=['GET'])
def register_page():
    """顯示註冊頁面

    - 若使用者已登入，重導向至 /dashboard
    - 渲染 auth/register.html
    """
    pass


@bp.route('/register', methods=['POST'])
def register():
    """處理帳號註冊

    輸入：表單欄位 email、password、password_confirm、nickname
    處理：
      1. 驗證密碼與確認密碼一致
      2. User.get_by_email(email) 檢查是否重複
      3. User.create(email, password, nickname) 建立帳號
      4. 成功 → 重導向 /auth/login 並 Flash「註冊成功」
    錯誤：Email 重複 → Flash「此 Email 已被註冊」
    """
    pass


@bp.route('/logout')
@login_required
def logout():
    """處理使用者登出

    處理：呼叫 logout_user() 清除 Session
    輸出：重導向 /auth/login
    """
    pass
