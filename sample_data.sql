INSERT INTO items (
    shop_id, denpyo_no, tag1, shohin_code, shohin_name, color, contents,
    packaging_shape, kokyaku_code, kokyaku_name, cost_price, selling_price,
    tax_status, nyuuka_code, syukka_code, course, higiri_flag, delivery_date,
    syukka_date, syukka_time, syukka_flag, seikyuu_flag, azukari_date,
    shiage_date, return_datetime, factory_staff_id, factory_staff_name,
    factory_location, factory_process_datetime, factory_comment, tag2,
    status, comment, image_path, signature_path, created_at, updated_at
) VALUES (
    1, 'DEN001', 'TAG1', 'SHO001', '商品名1', '赤', '内容1',
    '箱', 'KOK001', '顧客名1', 1000.00, 2000.00,
    '税込', 'NYU001', 'SYU001', 'コース1', 0, '2025-04-13 00:00:00',
    '2025-04-13 00:00:00', '午前', 0, 0, '2025-04-13 00:00:00',
    '2025-04-13 00:00:00', '2025-04-13 00:00:00', 'STAFF001', 'スタッフ名1',
    '工場1', '2025-04-13 00:00:00', 'コメント1', 'TAG2',
    'ステータス1', 'コメント1', '/path/to/image1.jpg', '/path/to/signature1.jpg',
    NOW(), NOW()
);