-- Tạo database
CREATE DATABASE IF NOT EXISTS authen
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE authen;

-- Bảng users
CREATE TABLE IF NOT EXISTS users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id VARCHAR(190) NOT NULL,                 -- có thể là username, email, hoặc UUID
  trang_thai TINYINT(1) NOT NULL DEFAULT 0,      -- 0 = chưa mua vé, 1 = đã mua vé
  mat_khau VARCHAR(255) NOT NULL,                -- lưu HASH (bcrypt/argon2), KHÔNG lưu plain text
  diem_thuong INT UNSIGNED NOT NULL DEFAULT 0,   -- điểm thưởng tích lũy
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dữ liệu mẫu (mat_khau dưới đây là ví dụ hash bcrypt, KHÔNG dùng thật)
-- '$2y$12$example...' chỉ là minh họa, bạn thay bằng hash thật từ app
INSERT INTO users (user_id, trang_thai, mat_khau, diem_thuong) VALUES
('khoa', 1, '$2y$12$examplebcrypthashxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 120),
('an',   0, '$2y$12$examplebcrypthashyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy',  15);

-- Một số truy vấn mẫu
-- 1) Kiểm tra user đã mua vé chưa
SELECT user_id, trang_thai FROM users WHERE user_id = 'khoa';

-- 2) Cộng điểm thưởng sau khi mua vé
UPDATE users SET diem_thuong = diem_thuong + 50 WHERE user_id = 'khoa';

-- 3) Đánh dấu đã mua vé
UPDATE users SET trang_thai = 1 WHERE user_id = 'an';

-- 4) Đổi mật khẩu (đặt hash mới)
UPDATE users SET mat_khau = '$2y$12$hashmoi.........................' WHERE user_id = 'khoa';
