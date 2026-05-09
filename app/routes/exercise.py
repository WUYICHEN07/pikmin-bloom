"""運動數據路由 — 數據輸入、轉換提交、歷史紀錄"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

bp = Blueprint('exercise', __name__, url_prefix='/exercise')


@bp.route('/input', methods=['GET'])
@login_required
def input_page():
    """顯示運動數據輸入頁面

    處理：
      1. ConversionRule.get_active_rules() → 取得可用運動類型列表
      2. 讀取 current_user.last_exercise_type → 預填上次選擇
    輸出：渲染 exercise/input.html，傳入運動類型列表
    """
    pass


@bp.route('/convert', methods=['POST'])
@login_required
def convert():
    """提交運動數據並執行步數轉換

    輸入：表單欄位 exercise_type、intensity、duration_minutes、
          stroke_count、distance_meters、exercise_date
    處理：
      1. DataValidator 驗證數據格式與範圍
      2. Exercise.create(...) → 儲存原始運動紀錄
      3. ConversionEngine.convert(exercise) → 執行步數轉換
      4. Conversion.create(...) → 儲存轉換結果
      5. 更新 current_user.last_exercise_type / last_intensity
    輸出：重導向 /conversion/result/<conversion_id>
    錯誤：驗證失敗 → Flash 錯誤，重導向 /exercise/input
          轉換規則不存在 → 404
    """
    pass


@bp.route('/history', methods=['GET'])
@login_required
def history():
    """顯示運動紀錄歷史列表

    輸入：可選查詢參數 page（分頁用）
    處理：
      1. Exercise.get_by_user_id(user_id) → 取得使用者所有紀錄
      2. 透過關聯載入對應的 Conversion 結果
    輸出：渲染 exercise/history.html，傳入紀錄列表
    """
    pass


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """刪除指定運動紀錄

    輸入：URL 參數 id（運動紀錄 ID）
    處理：
      1. Exercise.get_by_id(id) → 查詢紀錄
      2. 驗證紀錄歸屬 current_user（否則 403）
      3. exercise.delete() → 刪除紀錄（Cascade 刪除關聯轉換）
    輸出：重導向 /exercise/history，Flash「紀錄已刪除」
    錯誤：紀錄不存在 → 404；非本人紀錄 → 403
    """
    pass
