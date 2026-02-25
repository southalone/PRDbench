-- 图书馆管理系统数据备份
-- 生成时间: 2023-01-01 12:00:00

-- 用户表数据
INSERT INTO user (StudentId, Name, Password, IsAdmin, tel) VALUES
('admin', '系统管理员', 'e10adc3949ba59abbe56e057f20f883e', 1, 'admin@library.com'),
('TEST001', '测试用户', 'e10adc3949ba59abbe56e057f20f883e', 0, 'test@email.com');

-- 图书表数据
INSERT INTO book (BookId, BookName, Auth, Category, Publisher, PublishTime, NumStorage, NumCanBorrow, NumBookinged) VALUES
('ISBN001', 'Python编程入门', '张三', '计算机', '人民出版社', '2023-01-01', 10, 8, 0);

-- 借阅表数据
INSERT INTO user_book (StudentId, BookId, BorrowTime, ReturnTime, BorrowState, BookingState) VALUES
('TEST001', 'ISBN001', '2023-01-01', NULL, 1, 0);
