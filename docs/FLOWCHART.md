# 流程圖設計 — 皮克敏水性類型運動換算步數系統

> **文件版本**：v1.0  
> **建立日期**：2026-05-09  
> **對應文件**：docs/PRD.md、docs/ARCHITECTURE.md  

---

## 1. 使用者流程圖（User Flow）

### 1.1 整體操作流程

從使用者進入網站到完成核心操作的完整路徑：

```mermaid
flowchart LR
    A([🏊 使用者開啟網頁]) --> B{已登入？}

    B -->|否| C[登入頁面]
    C --> D{有帳號？}
    D -->|否| E[註冊頁面]
    E --> F[填寫帳號/密碼/暱稱]
    F --> G[註冊成功]
    G --> C
    D -->|是| H[輸入帳號密碼]
    H --> I{驗證成功？}
    I -->|否| H
    I -->|是| J[📊 進度追蹤看板]

    B -->|是| J

    J --> K{要執行什麼操作？}

    K -->|一鍵快速轉換| L[⚡ 快速轉換頁面]
    K -->|手動輸入數據| M[🏊 運動數據輸入]
    K -->|查看歷史紀錄| N[📋 運動紀錄歷史]
    K -->|個人設定| O[⚙️ 設定頁面]
    K -->|登出| P([登出系統])
```

### 1.2 運動數據輸入與步數轉換流程

```mermaid
flowchart LR
    A([選擇輸入方式]) --> B{輸入方式？}

    B -->|手動輸入| C[選擇運動類型]
    C --> D[輸入運動數據]
    D --> E[選擇運動強度]
    E --> F[預覽數據]

    B -->|一鍵快速轉換| G[使用上次設定]
    G --> F

    B -->|匯入檔案| H[上傳 CSV/JSON]
    H --> I{檔案格式正確？}
    I -->|否| J[顯示錯誤訊息]
    J --> H
    I -->|是| F

    F --> K[確認送出]
    K --> L{數據驗證通過？}
    L -->|否| M[顯示驗證錯誤]
    M --> D
    L -->|是| N[⚙️ 轉換引擎計算]
    N --> O[🎯 顯示轉換結果]
    O --> P[動畫展示步數]
    P --> Q{下一步？}
    Q -->|繼續輸入| A
    Q -->|查看看板| R[📊 進度追蹤看板]
    Q -->|查看歷史| S[📋 運動紀錄歷史]
```

### 1.3 個人設定與背景主題切換流程

```mermaid
flowchart LR
    A([進入設定頁面]) --> B{設定項目？}

    B -->|個人資料| C[修改暱稱/運動類型]
    C --> D[儲存變更]
    D --> E[顯示成功訊息]

    B -->|背景主題| F[瀏覽主題列表]
    F --> G[即時預覽主題]
    G --> H{確認切換？}
    H -->|否| F
    H -->|是| I[套用新主題]
    I --> E

    B -->|資料匯出| J[選擇匯出範圍]
    J --> K[產生 CSV 檔案]
    K --> L[下載檔案]

    E --> M([返回看板])
    L --> M
```

---

## 2. 系統序列圖（Sequence Diagram）

### 2.1 使用者註冊流程

```mermaid
sequenceDiagram
    actor User as 🏊 使用者
    participant Browser as 🌐 瀏覽器
    participant Route as 🎮 Flask Route<br/>auth.py
    participant Model as 📦 User Model
    participant DB as 💾 SQLite

    User->>Browser: 點擊「註冊」
    Browser->>Route: GET /auth/register
    Route-->>Browser: 渲染 register.html

    User->>Browser: 填寫帳號、密碼、暱稱並送出
    Browser->>Route: POST /auth/register

    Route->>Route: 驗證表單資料（CSRF Token）
    Route->>Model: 檢查帳號是否已存在
    Model->>DB: SELECT FROM users WHERE email=?
    DB-->>Model: 查詢結果

    alt 帳號已存在
        Model-->>Route: 帳號重複
        Route-->>Browser: 顯示錯誤訊息
    else 帳號可用
        Route->>Route: bcrypt 加密密碼
        Route->>Model: 建立新使用者
        Model->>DB: INSERT INTO users
        DB-->>Model: 成功
        Model-->>Route: 使用者已建立
        Route-->>Browser: 重導向至登入頁
        Browser-->>User: 顯示「註冊成功，請登入」
    end
```

### 2.2 使用者登入流程

```mermaid
sequenceDiagram
    actor User as 🏊 使用者
    participant Browser as 🌐 瀏覽器
    participant Route as 🎮 Flask Route<br/>auth.py
    participant Login as 🔐 Flask-Login
    participant Model as 📦 User Model
    participant DB as 💾 SQLite

    User->>Browser: 點擊「登入」
    Browser->>Route: GET /auth/login
    Route-->>Browser: 渲染 login.html

    User->>Browser: 輸入帳號密碼並送出
    Browser->>Route: POST /auth/login

    Route->>Model: 查詢使用者
    Model->>DB: SELECT FROM users WHERE email=?
    DB-->>Model: 使用者資料

    alt 使用者不存在或密碼錯誤
        Route->>Route: bcrypt 驗證失敗
        Route-->>Browser: 顯示「帳號或密碼錯誤」
    else 驗證成功
        Route->>Route: bcrypt 驗證通過
        Route->>Login: login_user(user)
        Login-->>Route: Session 已建立
        Route-->>Browser: 重導向至進度看板
        Browser-->>User: 顯示進度追蹤看板 📊
    end
```

### 2.3 步數轉換核心流程（手動輸入）

```mermaid
sequenceDiagram
    actor User as 🏊 使用者
    participant Browser as 🌐 瀏覽器
    participant Route as 🎮 Flask Route<br/>exercise.py
    participant Validator as ✅ DataValidator
    participant Engine as ⚙️ ConversionEngine
    participant ExModel as 📦 Exercise Model
    participant ConvModel as 📦 Conversion Model
    participant RuleModel as 📦 ConversionRule Model
    participant DB as 💾 SQLite

    User->>Browser: 選擇運動類型、輸入數據、選擇強度
    Browser->>Route: POST /exercise/convert

    Route->>Validator: 驗證數據格式與範圍
    alt 驗證失敗
        Validator-->>Route: 錯誤訊息
        Route-->>Browser: 顯示驗證錯誤
    else 驗證通過
        Validator-->>Route: 驗證通過 ✓

        Route->>ExModel: 儲存原始運動紀錄
        ExModel->>DB: INSERT INTO exercises
        DB-->>ExModel: exercise_id

        Route->>Engine: 呼叫轉換引擎
        Engine->>RuleModel: 查詢轉換規則
        RuleModel->>DB: SELECT FROM conversion_rules WHERE type=?
        DB-->>RuleModel: 轉換係數與公式
        RuleModel-->>Engine: 轉換規則資料

        Engine->>Engine: 計算步數 = 基準值 × 時間 × 強度係數
        Engine-->>Route: 轉換結果（步數）

        Route->>ConvModel: 儲存轉換紀錄
        ConvModel->>DB: INSERT INTO conversions
        DB-->>ConvModel: conversion_id

        Route-->>Browser: 渲染 result.html（含動畫）
        Browser-->>User: 顯示轉換結果 🎯🎉
    end
```

### 2.4 一鍵快速轉換流程

```mermaid
sequenceDiagram
    actor User as 🏊 使用者
    participant Browser as 🌐 瀏覽器
    participant Route as 🎮 Flask Route<br/>conversion.py
    participant Model as 📦 User Model
    participant Engine as ⚙️ ConversionEngine
    participant DB as 💾 SQLite

    User->>Browser: 點擊「⚡ 一鍵快速轉換」
    Browser->>Route: GET /conversion/quick

    Route->>Model: 查詢使用者上次運動設定
    Model->>DB: SELECT last_exercise_type, last_intensity FROM users
    DB-->>Model: 上次設定

    Route-->>Browser: 渲染快速輸入頁面（預填上次設定）
    User->>Browser: 確認或微調數據，點擊送出
    Browser->>Route: POST /conversion/quick

    Route->>Engine: 使用預設設定進行轉換
    Engine-->>Route: 轉換結果

    Route->>DB: 儲存運動紀錄與轉換紀錄
    DB-->>Route: 成功

    Route->>Model: 更新使用者最後使用設定
    Model->>DB: UPDATE users SET last_exercise_type=?
    DB-->>Model: 成功

    Route-->>Browser: 渲染結果頁面
    Browser-->>User: 顯示轉換結果 ⚡🎉
```

### 2.5 進度看板數據載入流程

```mermaid
sequenceDiagram
    actor User as 🏊 使用者
    participant Browser as 🌐 瀏覽器
    participant Route as 🎮 Flask Route<br/>dashboard.py
    participant ConvModel as 📦 Conversion Model
    participant ExModel as 📦 Exercise Model
    participant DB as 💾 SQLite

    User->>Browser: 進入進度追蹤看板
    Browser->>Route: GET /dashboard

    Route->>ConvModel: 查詢今日累計步數
    ConvModel->>DB: SELECT SUM(steps) FROM conversions WHERE date=TODAY
    DB-->>ConvModel: 今日步數

    Route->>ConvModel: 查詢本週/本月累計
    ConvModel->>DB: SELECT SUM(steps) GROUP BY period
    DB-->>ConvModel: 週/月統計

    Route->>ExModel: 查詢歷史運動數據（圖表用）
    ExModel->>DB: SELECT date, steps FROM conversions ORDER BY date
    DB-->>ExModel: 歷史數據

    Route->>Route: 計算目標達成率

    Route-->>Browser: 渲染 dashboard/index.html
    Note over Browser: Chart.js 繪製折線圖/柱狀圖
    Browser-->>User: 顯示完整進度看板 📊
```

---

## 3. 功能清單對照表

### 3.1 認證相關（auth）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
|------|---------|-----------|------|
| 顯示登入頁面 | `/auth/login` | GET | 渲染登入表單 |
| 登入驗證 | `/auth/login` | POST | 驗證帳密，建立 Session |
| 顯示註冊頁面 | `/auth/register` | GET | 渲染註冊表單 |
| 註冊帳號 | `/auth/register` | POST | 建立新使用者帳號 |
| 登出 | `/auth/logout` | GET | 清除 Session，重導登入頁 |

### 3.2 進度看板（dashboard）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
|------|---------|-----------|------|
| 看板首頁 | `/dashboard` | GET | 顯示累計步數、目標達成率、圖表 |

### 3.3 運動數據（exercise）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
|------|---------|-----------|------|
| 運動數據輸入頁 | `/exercise/input` | GET | 渲染運動數據輸入表單 |
| 提交運動數據並轉換 | `/exercise/convert` | POST | 驗證數據 → 儲存 → 轉換 → 顯示結果 |
| 運動紀錄歷史 | `/exercise/history` | GET | 顯示所有歷史運動紀錄與轉換結果 |
| 刪除運動紀錄 | `/exercise/<id>/delete` | POST | 刪除指定運動紀錄及對應轉換 |

### 3.4 步數轉換（conversion）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
|------|---------|-----------|------|
| 一鍵快速轉換頁面 | `/conversion/quick` | GET | 預填上次設定的快速輸入頁 |
| 執行快速轉換 | `/conversion/quick` | POST | 使用預設設定進行轉換 |
| 轉換結果頁面 | `/conversion/result/<id>` | GET | 顯示指定轉換結果（含動畫） |

### 3.5 個人設定（settings）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
|------|---------|-----------|------|
| 設定頁面 | `/settings` | GET | 顯示個人設定選項 |
| 更新個人資料 | `/settings/profile` | POST | 修改暱稱、慣用運動類型 |
| 切換背景主題 | `/settings/theme` | POST | 更新使用者偏好主題 |
| 匯出運動數據 | `/settings/export` | GET | 產生並下載 CSV 匯出檔 |

### 3.6 路由總覽

```
/auth/login          GET, POST    ← 登入
/auth/register       GET, POST    ← 註冊
/auth/logout         GET          ← 登出

/dashboard           GET          ← 進度看板（首頁）

/exercise/input      GET          ← 運動數據輸入
/exercise/convert    POST         ← 提交並轉換
/exercise/history    GET          ← 歷史紀錄
/exercise/<id>/delete POST        ← 刪除紀錄

/conversion/quick    GET, POST    ← 一鍵快速轉換
/conversion/result/<id> GET       ← 轉換結果

/settings            GET          ← 設定頁面
/settings/profile    POST         ← 更新資料
/settings/theme      POST         ← 切換主題
/settings/export     GET          ← 匯出數據
```

---

*文件結束 — 所有 Mermaid 圖表可直接在 GitHub 或支援 Mermaid 的編輯器中預覽*
