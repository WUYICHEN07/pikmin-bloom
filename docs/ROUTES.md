# 路由設計 — 皮克敏水性類型運動換算步數系統

> **文件版本**：v1.0  
> **建立日期**：2026-05-09  
> **對應文件**：docs/PRD.md、docs/ARCHITECTURE.md、docs/DB_DESIGN.md  

---

## 1. 路由總覽表格

### 1.1 認證模組（auth）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|-----------|---------|---------|------|
| 登入頁面 | GET | `/auth/login` | `auth/login.html` | 顯示登入表單 |
| 登入驗證 | POST | `/auth/login` | — | 驗證帳密，成功重導向看板 |
| 註冊頁面 | GET | `/auth/register` | `auth/register.html` | 顯示註冊表單 |
| 建立帳號 | POST | `/auth/register` | — | 建立使用者，重導向登入頁 |
| 登出 | GET | `/auth/logout` | — | 清除 Session，重導向登入頁 |

### 1.2 進度看板模組（dashboard）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|-----------|---------|---------|------|
| 看板首頁 | GET | `/dashboard` | `dashboard/index.html` | 顯示步數統計、圖表、目標達成率 |

### 1.3 運動數據模組（exercise）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|-----------|---------|---------|------|
| 數據輸入頁面 | GET | `/exercise/input` | `exercise/input.html` | 顯示運動數據輸入表單 |
| 提交並轉換 | POST | `/exercise/convert` | — | 驗證 → 儲存 → 轉換 → 重導向結果頁 |
| 歷史紀錄列表 | GET | `/exercise/history` | `exercise/history.html` | 顯示所有運動與轉換紀錄 |
| 刪除紀錄 | POST | `/exercise/<id>/delete` | — | 刪除運動紀錄，重導向歷史頁 |

### 1.4 步數轉換模組（conversion）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|-----------|---------|---------|------|
| 快速轉換頁面 | GET | `/conversion/quick` | `conversion/quick.html` | 預填上次設定的簡化輸入頁 |
| 執行快速轉換 | POST | `/conversion/quick` | — | 快速轉換，重導向結果頁 |
| 轉換結果 | GET | `/conversion/result/<id>` | `conversion/result.html` | 顯示轉換結果（含動畫） |

### 1.5 個人設定模組（settings）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|-----------|---------|---------|------|
| 設定頁面 | GET | `/settings` | `settings/index.html` | 顯示個人設定選項 |
| 更新個人資料 | POST | `/settings/profile` | — | 修改暱稱與運動偏好 |
| 切換背景主題 | POST | `/settings/theme` | — | 更新偏好主題 |
| 匯出數據 | GET | `/settings/export` | — | 產生並下載 CSV 檔案 |

---

## 2. 每個路由的詳細說明

### 2.1 認證模組

#### `GET /auth/login` — 登入頁面

- **輸入**：無（可接收 `next` 查詢參數）
- **處理邏輯**：若已登入則重導向 `/dashboard`，否則渲染登入表單
- **輸出**：渲染 `auth/login.html`
- **錯誤處理**：無

#### `POST /auth/login` — 登入驗證

- **輸入**：表單欄位 `email`、`password`
- **處理邏輯**：
  1. 呼叫 `User.get_by_email(email)` 查詢使用者
  2. 呼叫 `user.check_password(password)` 驗證密碼
  3. 成功：`login_user(user)`，重導向 `/dashboard`
  4. 失敗：Flash 錯誤訊息
- **輸出**：成功 → 重導向 `/dashboard`；失敗 → 重新渲染 `auth/login.html`
- **錯誤處理**：帳號不存在或密碼錯誤 → Flash「帳號或密碼錯誤」

#### `GET /auth/register` — 註冊頁面

- **輸入**：無
- **處理邏輯**：若已登入則重導向 `/dashboard`，否則渲染註冊表單
- **輸出**：渲染 `auth/register.html`
- **錯誤處理**：無

#### `POST /auth/register` — 建立帳號

- **輸入**：表單欄位 `email`、`password`、`password_confirm`、`nickname`
- **處理邏輯**：
  1. 驗證密碼與確認密碼是否一致
  2. 呼叫 `User.get_by_email(email)` 檢查是否重複
  3. 呼叫 `User.create(email, password, nickname)` 建立帳號
- **輸出**：成功 → 重導向 `/auth/login` 並 Flash「註冊成功」
- **錯誤處理**：Email 重複 → Flash「此 Email 已被註冊」；密碼不一致 → Flash 提示

#### `GET /auth/logout` — 登出

- **輸入**：無
- **處理邏輯**：呼叫 `logout_user()`，清除 Session
- **輸出**：重導向 `/auth/login`
- **錯誤處理**：無

---

### 2.2 進度看板模組

#### `GET /dashboard` — 看板首頁

- **輸入**：無（從 `current_user` 取得 `user_id`）
- **處理邏輯**：
  1. 呼叫 `Conversion.get_today_steps(user_id)` 取得今日步數
  2. 呼叫 `Conversion.get_weekly_steps(user_id)` 取得本週步數
  3. 呼叫 `Conversion.get_monthly_steps(user_id)` 取得本月步數
  4. 呼叫 `Conversion.get_total_steps(user_id)` 取得累計總步數
  5. 呼叫 `Conversion.get_daily_summary(user_id, 30)` 取得圖表數據
- **輸出**：渲染 `dashboard/index.html`，傳入統計數據與圖表資料
- **錯誤處理**：需 `@login_required`

---

### 2.3 運動數據模組

#### `GET /exercise/input` — 數據輸入頁面

- **輸入**：無
- **處理邏輯**：
  1. 呼叫 `ConversionRule.get_active_rules()` 取得可用運動類型
  2. 讀取 `current_user.last_exercise_type` 預填上次選擇
- **輸出**：渲染 `exercise/input.html`，傳入運動類型列表
- **錯誤處理**：需 `@login_required`

#### `POST /exercise/convert` — 提交並轉換

- **輸入**：表單欄位 `exercise_type`、`intensity`、`duration_minutes`、`stroke_count`、`distance_meters`、`exercise_date`
- **處理邏輯**：
  1. 呼叫 `DataValidator` 驗證數據格式與範圍
  2. 呼叫 `Exercise.create(...)` 儲存原始運動紀錄
  3. 呼叫 `ConversionEngine.convert(exercise)` 執行步數轉換
  4. 呼叫 `Conversion.create(...)` 儲存轉換結果
  5. 更新 `current_user.last_exercise_type` 與 `last_intensity`
- **輸出**：重導向 `/conversion/result/<conversion_id>`
- **錯誤處理**：驗證失敗 → Flash 錯誤並重導回輸入頁；轉換規則不存在 → 404

#### `GET /exercise/history` — 歷史紀錄列表

- **輸入**：可選查詢參數 `page`（分頁）
- **處理邏輯**：
  1. 呼叫 `Exercise.get_by_user_id(user_id)` 取得紀錄
  2. 透過關聯載入對應的 `Conversion` 結果
- **輸出**：渲染 `exercise/history.html`，傳入紀錄列表
- **錯誤處理**：需 `@login_required`

#### `POST /exercise/<id>/delete` — 刪除紀錄

- **輸入**：URL 參數 `id`（運動紀錄 ID）
- **處理邏輯**：
  1. 呼叫 `Exercise.get_by_id(id)` 查詢紀錄
  2. 驗證紀錄歸屬 `current_user`
  3. 呼叫 `exercise.delete()` 刪除（Cascade 刪除關聯轉換紀錄）
- **輸出**：重導向 `/exercise/history` 並 Flash「紀錄已刪除」
- **錯誤處理**：紀錄不存在 → 404；非本人紀錄 → 403

---

### 2.4 步數轉換模組

#### `GET /conversion/quick` — 快速轉換頁面

- **輸入**：無
- **處理邏輯**：
  1. 讀取 `current_user.last_exercise_type` 與 `last_intensity`
  2. 呼叫 `ConversionRule.get_active_rules()` 取得運動類型
- **輸出**：渲染 `conversion/quick.html`，預填上次設定
- **錯誤處理**：需 `@login_required`；無歷史設定 → 使用預設值

#### `POST /conversion/quick` — 執行快速轉換

- **輸入**：表單欄位（同 `POST /exercise/convert`）
- **處理邏輯**：與 `POST /exercise/convert` 相同
- **輸出**：重導向 `/conversion/result/<conversion_id>`
- **錯誤處理**：同 `POST /exercise/convert`

#### `GET /conversion/result/<id>` — 轉換結果

- **輸入**：URL 參數 `id`（轉換紀錄 ID）
- **處理邏輯**：
  1. 呼叫 `Conversion.get_by_id(id)` 查詢轉換結果
  2. 透過關聯載入 `Exercise` 與 `ConversionRule` 資訊
- **輸出**：渲染 `conversion/result.html`，含動畫效果數據
- **錯誤處理**：紀錄不存在 → 404；非本人紀錄 → 403

---

### 2.5 個人設定模組

#### `GET /settings` — 設定頁面

- **輸入**：無
- **處理邏輯**：讀取 `current_user` 的個人資料與偏好
- **輸出**：渲染 `settings/index.html`
- **錯誤處理**：需 `@login_required`

#### `POST /settings/profile` — 更新個人資料

- **輸入**：表單欄位 `nickname`、`preferred_sport`
- **處理邏輯**：呼叫 `current_user.update(nickname=..., preferred_sport=...)`
- **輸出**：重導向 `/settings` 並 Flash「資料已更新」
- **錯誤處理**：驗證失敗 → Flash 錯誤

#### `POST /settings/theme` — 切換背景主題

- **輸入**：表單欄位 `theme`（ocean / lake / pool / river）
- **處理邏輯**：呼叫 `current_user.update(preferred_theme=theme)`
- **輸出**：重導向 `/settings` 並 Flash「主題已切換」
- **錯誤處理**：無效主題名稱 → Flash 錯誤

#### `GET /settings/export` — 匯出數據

- **輸入**：可選查詢參數 `format`（預設 `csv`）
- **處理邏輯**：
  1. 呼叫 `Exercise.get_by_user_id(user_id)` 取得所有紀錄
  2. 組合 `Conversion` 結果，產生 CSV 內容
  3. 設定 HTTP Header `Content-Disposition: attachment`
- **輸出**：回傳 CSV 檔案下載
- **錯誤處理**：無紀錄 → Flash「尚無可匯出的紀錄」

---

## 3. Jinja2 模板清單

所有模板皆繼承 `base.html` 基底模板。

| 模板路徑 | 繼承自 | 說明 |
|---------|--------|------|
| `templates/base.html` | — | 基底模板：HTML head、導覽列、Flash 訊息區、footer、主題 CSS 載入 |
| `templates/auth/login.html` | `base.html` | 登入表單（Email + 密碼） |
| `templates/auth/register.html` | `base.html` | 註冊表單（Email + 密碼 + 確認密碼 + 暱稱） |
| `templates/dashboard/index.html` | `base.html` | 進度看板：步數統計卡片、Chart.js 圖表、目標達成進度條 |
| `templates/exercise/input.html` | `base.html` | 運動數據輸入表單（運動類型下拉、強度選擇、數值輸入） |
| `templates/exercise/history.html` | `base.html` | 運動紀錄列表（表格含排序、刪除按鈕） |
| `templates/conversion/quick.html` | `base.html` | 快速轉換頁面（預填設定、大按鈕操作） |
| `templates/conversion/result.html` | `base.html` | 轉換結果展示（步數動畫、詳細計算過程） |
| `templates/settings/index.html` | `base.html` | 設定頁面（個人資料表單、主題預覽、匯出按鈕） |
| `templates/errors/404.html` | `base.html` | 404 錯誤頁面 |
| `templates/errors/403.html` | `base.html` | 403 錯誤頁面 |

---

## 4. 路由骨架程式碼

路由骨架檔案位於 `app/routes/`，每個模組一個檔案。  
詳見各檔案內的函式定義與 docstring。

---

*文件結束 — 搭配 `app/routes/` 下的骨架程式碼一起閱讀*
