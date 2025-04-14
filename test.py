CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- 基本情報
    shop_id SMALLINT NOT NULL,              -- 店舗ID
    denpyo_no VARCHAR(20) NOT NULL,         -- 伝票番号
    tag1 VARCHAR(20),                        -- タグ1（tag）
    shohin_code VARCHAR(20) NOT NULL,       -- 商品コード
    shohin_name VARCHAR(50) NOT NULL,       -- 商品名
    color VARCHAR(20),                       -- 色
    contents VARCHAR(200),                   -- 商品内容
    packaging_shape VARCHAR(30),             -- 商品包装形状
    
    -- 顧客情報
    kokyaku_code VARCHAR(20),               -- 顧客コード
    kokyaku_name VARCHAR(50),               -- 顧客名
    
    -- 金額情報
    cost_price DECIMAL(10,2),                -- 原価（tanka）
    selling_price DECIMAL(10,2),             -- 売価（baika）
    tax_status VARCHAR(10),                  -- 内税/外税区分（mi_gai）
    
    -- 入出荷情報 
    nyuuka_code VARCHAR(20),               -- 入荷コード（nyuka）
    syukka_code VARCHAR(20),               -- 出荷コード（syukka）
    course VARCHAR(50),                    -- コース
    higiri_flag TINYINT(2) DEFAULT 0,      -- 期日フラグ（higiri_flag）
    delivery_date DATETIME,                -- 納期（nouki）
    syukka_date DATETIME,                  -- 出荷日（syukka_date）
    syukka_time VARCHAR(20),               -- 出荷便（syukka_bin）
    syukka_flag TINYINT(2) DEFAULT 0,      -- 出荷フラグ
    seikyuu_flag TINYINT(2) DEFAULT 0,     -- 請求フラグ（seikyuu_flag）
    
    -- 保管・処理情報
    azukari_date DATETIME,                   -- 預かり日（azukari_date）
    shiage_date DATETIME,                    -- 仕上げ日（shiage_date）
    return_datetime DATETIME,                -- 返却日時（henkyaku_datetime）
    
        -- 工場情報
    factory_staff VARCHAR(30),               -- 工場担当者（fact_person）
    factory_location VARCHAR(50),            -- 工場場所（fact_place）
    factory_process_datetime DATETIME,       -- 工場処理日時（fact_updatetime）
    factory_comment TEXT,                    -- 工場コメント（fact_comment）
    
    -- タグ情報補足
    tag2 VARCHAR(20),                        -- タグ2
    
    -- その他
    status VARCHAR(20),                      -- 状態（torikeshiを含む）
    comment TEXT,                            -- コメント
    image_path VARCHAR(255),                 -- 画像パス（gazou）
    signature_path VARCHAR(255),             -- 署名パス（sign）
    
    -- 監査情報
    created_at DATETIME NOT NULL,            -- 作成日時
    updated_at DATETIME NOT NULL,            -- 更新日時
    
    -- インデックス
    INDEX idx_shop_receipt (shop_id, denpyo_no),
    INDEX idx_kokyaku (kokyaku_code),
    INDEX idx_shohin (shohin_code),
    INDEX idx_dates (syukka_date, deposit_date, completion_date),
    INDEX idx_status (status)
);