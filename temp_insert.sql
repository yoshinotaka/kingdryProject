INSERT INTO items (
    shop_id, denpyo_no, tag1, shohin_code, shohin_name, color, contents,
    packaging_shape, kokyaku_code, kokyaku_name, cost_price, selling_price,
    tax_status, nyuuka_code, syukka_code, course, higiri_flag, delivery_date,
    syukka_date, syukka_time, syukka_flag, seikyuu_flag, azukari_date,
    shiage_date, return_datetime, factory_staff_id, factory_staff_name,
    factory_location, factory_process_datetime, factory_comment, tag2,
    status, comment, image_path, signature_path, created_at, updated_at
) VALUES
-- サンプルデータ1
(1, 'D2024001', 'TAG001', 'P001', '商品A', '赤', '商品Aの説明',
 '箱', 'C001', '顧客A', 1000.00, 2000.00, '内税', 'N001', 'S001',
 '通常便', 0, '2024-04-15 10:00:00', NULL, NULL, 0, 0,
 '2024-04-10 09:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 'TAG2-001', '未出荷', 'コメント1', '/images/p001.jpg', '/signatures/s001.png',
 NOW(), NOW()),

-- サンプルデータ2
(1, 'D2024002', 'TAG002', 'P002', '商品B', '青', '商品Bの説明',
 '袋', 'C002', '顧客B', 1500.00, 3000.00, '外税', 'N002', 'S002',
 '特急便', 1, '2024-04-16 15:00:00', NULL, NULL, 0, 0,
 '2024-04-11 10:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 'TAG2-002', '未出荷', 'コメント2', '/images/p002.jpg', '/signatures/s002.png',
 NOW(), NOW()),

-- サンプルデータ3
(2, 'D2024003', 'TAG003', 'P003', '商品C', '緑', '商品Cの説明',
 '箱', 'C003', '顧客C', 2000.00, 4000.00, '内税', 'N003', 'S003',
 '通常便', 0, '2024-04-17 11:00:00', NULL, NULL, 0, 0,
 '2024-04-12 11:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
 'TAG2-003', '未出荷', 'コメント3', '/images/p003.jpg', '/signatures/s003.png',
 NOW(), NOW()); 