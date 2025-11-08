-- ✅ Tạo bảng checkin (không tạo database)
CREATE TABLE IF NOT EXISTS checkin (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user VARCHAR(190) NOT NULL,
  dia_diem VARCHAR(255) NOT NULL,
  checkin TINYINT(1) NOT NULL DEFAULT 0,   -- 0 = chưa, 1 = đã
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_dia_diem (user, dia_diem)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ✅ Dữ liệu mẫu: nhiều địa điểm, nhiều người
INSERT INTO checkin (user, dia_diem, checkin) VALUES
('khoa', 'Bảo tàng Chứng tích Chiến tranh', 1),
('khoa', 'Dinh Độc Lập', 0),
('khoa', 'Nhà thờ Đức Bà', 1),
('khoa', 'Phố đi bộ Nguyễn Huệ', 1),
('khoa', 'Chợ Bến Thành', 1),
('khoa', 'Công viên Tao Đàn', 0),
('an', 'Bảo tàng Chứng tích Chiến tranh', 1),
('an', 'Chợ Bến Thành', 0),
('an', 'Phố đi bộ Nguyễn Huệ', 1),
('minh', 'Công viên Tao Đàn', 0),
('minh', 'Nhà thờ Đức Bà', 1),
('minh', 'Dinh Độc Lập', 1);
