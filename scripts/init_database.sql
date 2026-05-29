-- ============================================
-- 剩食猎人 数据库建表脚本
-- 数据库: food_saver_hunter
-- 版本: v3.0 (用户分离方案)
-- 日期: 2024
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS food_saver_hunter 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

USE food_saver_hunter;

-- ============================================
-- 1. 类型字典表 (先创建，被其他表引用)
-- ============================================

-- 店铺类型表
CREATE TABLE IF NOT EXISTS shop_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '类型名称',
    description VARCHAR(255) COMMENT '描述',
    icon VARCHAR(50) COMMENT '图标',
    color VARCHAR(20) DEFAULT '#1890FF' COMMENT '地图标注颜色',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='店铺类型表';

-- 食品类型表
CREATE TABLE IF NOT EXISTS food_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '类型名称',
    icon VARCHAR(50) COMMENT '图标',
    color VARCHAR(20) DEFAULT '#52C41A' COMMENT '地图标注颜色',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食品类型表';

-- ============================================
-- 2. 用户相关表
-- ============================================

-- 客户表
CREATE TABLE IF NOT EXISTS customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    phone VARCHAR(11) UNIQUE NOT NULL COMMENT '手机号',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    nickname VARCHAR(50) COMMENT '昵称',
    avatar VARCHAR(255) COMMENT '头像URL',
    points INT UNSIGNED DEFAULT 0 COMMENT '积分余额',
    carbon_saved DECIMAL(10,2) DEFAULT 0 COMMENT '累计减碳(kg)',
    food_saved DECIMAL(10,2) DEFAULT 0 COMMENT '累计救粮(kg)',
    total_orders INT UNSIGNED DEFAULT 0 COMMENT '累计订单数',
    hometown VARCHAR(100) COMMENT '老家位置',
    home_latitude DECIMAL(10,8) COMMENT '老家纬度',
    home_longitude DECIMAL(11,8) COMMENT '老家经度',
    privacy_public BOOLEAN DEFAULT TRUE COMMENT '是否公开环保数据',
    status ENUM('active', 'banned', 'deleted') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_phone (phone),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户表';

-- 商家表 (引用 shop_types)
CREATE TABLE IF NOT EXISTS merchants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    phone VARCHAR(11) UNIQUE NOT NULL COMMENT '手机号',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    store_name VARCHAR(100) NOT NULL COMMENT '店铺名称',
    store_type_id INT NOT NULL COMMENT '店铺类型ID',
    address VARCHAR(255) COMMENT '详细地址',
    latitude DECIMAL(10,8) COMMENT '纬度',
    longitude DECIMAL(11,8) COMMENT '经度',
    contact_phone VARCHAR(20) COMMENT '联系电话',
    business_hours VARCHAR(100) COMMENT '营业时间',
    business_license VARCHAR(255) COMMENT '营业执照URL',
    verified BOOLEAN DEFAULT FALSE COMMENT '是否认证',
    rating DECIMAL(2,1) DEFAULT 5.0 COMMENT '评分',
    total_orders INT UNSIGNED DEFAULT 0 COMMENT '累计订单数',
    status ENUM('active', 'banned', 'deleted') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_phone (phone),
    INDEX idx_store_type (store_type_id),
    INDEX idx_verified (verified),
    INDEX idx_status (status),
    FOREIGN KEY (store_type_id) REFERENCES shop_types(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商家表';

-- ============================================
-- 3. 店铺表
-- ============================================

-- 店铺表 (引用 merchants, shop_types)
CREATE TABLE IF NOT EXISTS shops (
    id INT PRIMARY KEY AUTO_INCREMENT,
    merchant_id INT NOT NULL COMMENT '商家ID',
    shop_type_id INT NOT NULL COMMENT '店铺类型ID',
    shop_name VARCHAR(100) NOT NULL COMMENT '店铺名称',
    address VARCHAR(255) COMMENT '详细地址',
    latitude DECIMAL(10,8) COMMENT '纬度',
    longitude DECIMAL(11,8) COMMENT '经度',
    contact_phone VARCHAR(20) COMMENT '联系电话',
    business_hours VARCHAR(100) COMMENT '营业时间',
    verified BOOLEAN DEFAULT FALSE COMMENT '是否认证',
    rating DECIMAL(2,1) DEFAULT 5.0 COMMENT '评分',
    total_orders INT UNSIGNED DEFAULT 0 COMMENT '累计订单数',
    status ENUM('active', 'closed', 'deleted') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_merchant (merchant_id),
    INDEX idx_shop_type (shop_type_id),
    INDEX idx_location (latitude, longitude),
    INDEX idx_verified (verified),
    INDEX idx_status (status),
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    FOREIGN KEY (shop_type_id) REFERENCES shop_types(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='店铺表';

-- ============================================
-- 4. 食品相关表
-- ============================================

-- 标准食品表 (引用 food_types)
CREATE TABLE IF NOT EXISTS foods (
    id INT PRIMARY KEY AUTO_INCREMENT,
    barcode VARCHAR(50) UNIQUE COMMENT '条形码',
    name VARCHAR(100) NOT NULL COMMENT '食品名称',
    food_type_id INT NOT NULL COMMENT '食品类型ID',
    brand VARCHAR(100) COMMENT '品牌',
    default_weight VARCHAR(50) COMMENT '默认规格',
    image_url VARCHAR(255) COMMENT '图片URL',
    avg_expiry_days INT DEFAULT 7 COMMENT '平均保质期(天)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_barcode (barcode),
    INDEX idx_food_type (food_type_id),
    INDEX idx_name (name),
    FOREIGN KEY (food_type_id) REFERENCES food_types(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标准食品表';

-- 食品口味标签表 (引用 foods)
CREATE TABLE IF NOT EXISTS food_flavor_tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    food_id INT NOT NULL COMMENT '食品ID',
    flavor_tag VARCHAR(20) NOT NULL COMMENT '口味标签',
    intensity TINYINT DEFAULT 5 COMMENT '强度1-10',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_food_flavor (food_id, flavor_tag),
    INDEX idx_food (food_id),
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食品口味标签表';

-- 店铺食品表 (引用 shops, foods)
CREATE TABLE IF NOT EXISTS shop_foods (
    id INT PRIMARY KEY AUTO_INCREMENT,
    shop_id INT NOT NULL COMMENT '店铺ID',
    food_id INT NOT NULL COMMENT '食品ID',
    shelf_position VARCHAR(50) COMMENT '货架位置',
    quantity INT DEFAULT 0 COMMENT '库存数量',
    original_price INT UNSIGNED COMMENT '原价(分)',
    discount_price INT UNSIGNED COMMENT '折扣价(分)',
    discount_type ENUM('none', 'mystery_box', 'clearance', 'time_limit') DEFAULT 'none' COMMENT '折扣类型',
    expiry_date DATE COMMENT '到期日期',
    risk_level ENUM('low', 'medium', 'high', 'critical') COMMENT '风险等级',
    status ENUM('draft', 'active', 'sold_out', 'expired') DEFAULT 'draft' COMMENT '状态',
    published_at DATETIME COMMENT '发布时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_shop_food_expiry (shop_id, food_id, expiry_date),
    INDEX idx_shop (shop_id),
    INDEX idx_food (food_id),
    INDEX idx_status (status),
    INDEX idx_expiry (expiry_date),
    INDEX idx_risk (risk_level),
    INDEX idx_discount_type (discount_type),
    FOREIGN KEY (shop_id) REFERENCES shops(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='店铺食品表';

-- ============================================
-- 5. 扫码相关表
-- ============================================

-- 用户扫码记录表 (引用 customers)
CREATE TABLE IF NOT EXISTS user_scans (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL COMMENT '客户ID',
    barcode VARCHAR(50) COMMENT '条形码',
    product_name VARCHAR(100) COMMENT '商品名称',
    expiry_date DATE COMMENT '到期日期',
    latitude DECIMAL(10,8) COMMENT '纬度',
    longitude DECIMAL(11,8) COMMENT '经度',
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' COMMENT '审核状态',
    points_earned INT DEFAULT 0 COMMENT '获得积分',
    rejection_reason VARCHAR(255) COMMENT '拒绝原因',
    audited_at DATETIME COMMENT '审核时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer (customer_id),
    INDEX idx_status (status),
    INDEX idx_barcode (barcode),
    INDEX idx_created (created_at),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户扫码记录表';

-- 扫码图片表 (引用 user_scans)
CREATE TABLE IF NOT EXISTS scan_images (
    id INT PRIMARY KEY AUTO_INCREMENT,
    scan_id INT NOT NULL COMMENT '扫码记录ID',
    image_url VARCHAR(255) NOT NULL COMMENT '图片URL',
    image_type ENUM('product', 'shelf', 'receipt') DEFAULT 'product' COMMENT '图片类型',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_scan (scan_id),
    FOREIGN KEY (scan_id) REFERENCES user_scans(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='扫码图片表';

-- ============================================
-- 6. 积分相关表
-- ============================================

-- 积分规则表
CREATE TABLE IF NOT EXISTS point_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    rule_type VARCHAR(50) NOT NULL COMMENT '规则类型',
    rule_name VARCHAR(100) NOT NULL COMMENT '规则名称',
    points INT NOT NULL COMMENT '积分数量',
    daily_limit INT COMMENT '每日上限',
    description VARCHAR(255) COMMENT '描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='积分规则表';

-- 积分变动记录表 (引用 customers)
CREATE TABLE IF NOT EXISTS hunter_points (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL COMMENT '客户ID',
    point_type ENUM('earn', 'spend', 'reward', 'refund', 'deduct') NOT NULL COMMENT '变动类型',
    amount INT NOT NULL COMMENT '变动数量',
    source VARCHAR(50) COMMENT '来源',
    source_id INT COMMENT '关联ID',
    description VARCHAR(255) COMMENT '描述',
    balance_after INT COMMENT '变动后余额',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer (customer_id),
    INDEX idx_type (point_type),
    INDEX idx_source (source, source_id),
    INDEX idx_created (created_at),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='积分变动记录表';

-- ============================================
-- 7. 订单相关表
-- ============================================

-- 订单表 (引用 customers, shop_foods)
CREATE TABLE IF NOT EXISTS orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL COMMENT '客户ID',
    shop_food_id INT COMMENT '店铺食品ID',
    quantity INT DEFAULT 1 COMMENT '数量',
    total_price INT UNSIGNED COMMENT '总价(分)',
    status ENUM('pending', 'paid', 'completed', 'cancelled', 'refunded') DEFAULT 'pending' COMMENT '状态',
    pickup_code VARCHAR(10) COMMENT '取货码',
    paid_at DATETIME COMMENT '支付时间',
    completed_at DATETIME COMMENT '完成时间',
    cancelled_at DATETIME COMMENT '取消时间',
    cancellation_reason VARCHAR(255) COMMENT '取消原因',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customer (customer_id),
    INDEX idx_shop_food (shop_food_id),
    INDEX idx_status (status),
    INDEX idx_pickup_code (pickup_code),
    INDEX idx_created (created_at),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (shop_food_id) REFERENCES shop_foods(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- ============================================
-- 8. 挑战相关表
-- ============================================

-- 挑战表
CREATE TABLE IF NOT EXISTS challenges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '挑战名称',
    description TEXT COMMENT '描述',
    target DECIMAL(10,2) NOT NULL COMMENT '目标值',
    unit VARCHAR(20) NOT NULL COMMENT '单位',
    reward_points INT UNSIGNED NOT NULL COMMENT '奖励积分',
    start_date DATE COMMENT '开始日期',
    end_date DATE COMMENT '结束日期',
    status ENUM('active', 'completed', 'expired') DEFAULT 'active' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_dates (start_date, end_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='挑战表';

-- 成就徽章表
CREATE TABLE IF NOT EXISTS badges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '徽章名称',
    description VARCHAR(255) COMMENT '描述',
    icon VARCHAR(255) COMMENT '图标URL',
    unlock_condition VARCHAR(255) COMMENT '解锁条件',
    reward_points INT UNSIGNED DEFAULT 0 COMMENT '奖励积分',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成就徽章表';

-- 用户挑战表 (引用 challenges, customers)
CREATE TABLE IF NOT EXISTS user_challenges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    challenge_id INT NOT NULL COMMENT '挑战ID',
    customer_id INT NOT NULL COMMENT '客户ID',
    current DECIMAL(10,2) DEFAULT 0 COMMENT '当前进度',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
    completed_at DATETIME COMMENT '完成时间',
    reward_claimed BOOLEAN DEFAULT FALSE COMMENT '奖励是否领取',
    UNIQUE KEY uk_challenge_customer (challenge_id, customer_id),
    INDEX idx_customer (customer_id),
    INDEX idx_challenge (challenge_id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户挑战表';

-- 用户徽章表 (引用 badges, customers)
CREATE TABLE IF NOT EXISTS user_badges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL COMMENT '客户ID',
    badge_id INT NOT NULL COMMENT '徽章ID',
    unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '解锁时间',
    reward_claimed BOOLEAN DEFAULT FALSE COMMENT '奖励是否领取',
    UNIQUE KEY uk_customer_badge (customer_id, badge_id),
    INDEX idx_customer (customer_id),
    INDEX idx_badge (badge_id),
    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户徽章表';

-- ============================================
-- 9. 推荐相关表
-- ============================================

-- 用户行为记录表 (引用 customers, foods, shop_foods)
CREATE TABLE IF NOT EXISTS customer_food_behaviors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL COMMENT '客户ID',
    food_id INT NOT NULL COMMENT '食品ID',
    shop_food_id INT COMMENT '店铺食品ID',
    behavior_type ENUM('purchase', 'scan', 'browse', 'favorite', 'reject', 'rating') NOT NULL COMMENT '行为类型',
    rating TINYINT COMMENT '评分1-5',
    context JSON COMMENT '上下文数据',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer (customer_id),
    INDEX idx_food (food_id),
    INDEX idx_behavior (behavior_type),
    INDEX idx_created (created_at),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE,
    FOREIGN KEY (shop_food_id) REFERENCES shop_foods(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户行为记录表';

-- 用户类别偏好表 (引用 customers, food_types)
CREATE TABLE IF NOT EXISTS customer_category_preferences (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL COMMENT '客户ID',
    food_type_id INT NOT NULL COMMENT '食品类型ID',
    preference_score DECIMAL(5,3) DEFAULT 0 COMMENT '偏好分数',
    purchase_count INT UNSIGNED DEFAULT 0 COMMENT '购买次数',
    total_spend INT UNSIGNED DEFAULT 0 COMMENT '总消费(分)',
    avg_rating DECIMAL(2,1) DEFAULT 0 COMMENT '平均评分',
    flavor_tags JSON COMMENT '口味标签',
    preferred_time_slots JSON COMMENT '偏好时间段',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_customer_category (customer_id, food_type_id),
    INDEX idx_customer (customer_id),
    INDEX idx_food_type (food_type_id),
    INDEX idx_score (preference_score DESC),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (food_type_id) REFERENCES food_types(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户类别偏好表';

-- 用户口味偏好表 (引用 customers)
CREATE TABLE IF NOT EXISTS customer_flavor_preferences (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL COMMENT '客户ID',
    flavor_tag VARCHAR(20) NOT NULL COMMENT '口味标签',
    preference_level ENUM('like', 'neutral', 'dislike') DEFAULT 'neutral' COMMENT '偏好级别',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_customer_flavor (customer_id, flavor_tag),
    INDEX idx_customer (customer_id),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户口味偏好表';

-- 用户手动偏好设置表 (引用 customers)
CREATE TABLE IF NOT EXISTS customer_manual_preferences (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT UNIQUE NOT NULL COMMENT '客户ID',
    favorite_types JSON COMMENT '喜欢的类型',
    favorite_flavors JSON COMMENT '喜欢的口味',
    disliked_ingredients JSON COMMENT '厌恶的食材',
    price_range_min INT UNSIGNED COMMENT '最低价格(分)',
    price_range_max INT UNSIGNED COMMENT '最高价格(分)',
    risk_preference ENUM('safe', 'normal', 'adventurous') DEFAULT 'normal' COMMENT '风险偏好',
    allergens JSON COMMENT '过敏原',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户手动偏好设置表';

-- 食品推荐表 (引用 customers, shop_foods)
CREATE TABLE IF NOT EXISTS food_recommendations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL COMMENT '客户ID',
    shop_food_id INT NOT NULL COMMENT '店铺食品ID',
    recommendation_score DECIMAL(5,3) COMMENT '推荐分数',
    category_match_score DECIMAL(5,3) DEFAULT 0 COMMENT '类型匹配分',
    distance_score DECIMAL(5,3) DEFAULT 0 COMMENT '距离分',
    risk_score DECIMAL(5,3) DEFAULT 0 COMMENT '风险适配分',
    discount_score DECIMAL(5,3) DEFAULT 0 COMMENT '折扣分',
    reason VARCHAR(100) COMMENT '推荐理由',
    scenario ENUM('personal', 'nearby', 'hot', 'new') DEFAULT 'personal' COMMENT '推荐场景',
    is_shown BOOLEAN DEFAULT TRUE COMMENT '是否展示',
    expires_at DATETIME COMMENT '过期时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer_score (customer_id, recommendation_score DESC),
    INDEX idx_shop_food (shop_food_id),
    INDEX idx_expires (expires_at),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (shop_food_id) REFERENCES shop_foods(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食品推荐表';

-- 推荐反馈表 (引用 customers, shop_foods)
CREATE TABLE IF NOT EXISTS recommendation_feedback (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL COMMENT '客户ID',
    shop_food_id INT NOT NULL COMMENT '店铺食品ID',
    feedback_type ENUM('click', 'purchase', 'ignore', 'hide') NOT NULL COMMENT '反馈类型',
    recommendation_score DECIMAL(5,3) COMMENT '推荐时的分数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer (customer_id),
    INDEX idx_shop_food (shop_food_id),
    INDEX idx_feedback (feedback_type),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (shop_food_id) REFERENCES shop_foods(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='推荐反馈表';

-- ============================================
-- 10. 通知相关表
-- ============================================

-- 通知表 (引用 customers, merchants)
CREATE TABLE IF NOT EXISTS notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT COMMENT '客户ID',
    merchant_id INT COMMENT '商家ID',
    title VARCHAR(100) NOT NULL COMMENT '标题',
    content TEXT COMMENT '内容',
    notification_type ENUM('system', 'order', 'challenge', 'point', 'recommendation') NOT NULL COMMENT '类型',
    related_id INT COMMENT '关联ID',
    is_read BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer (customer_id),
    INDEX idx_merchant (merchant_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created (created_at),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通知表';

-- ============================================
-- 11. AI相关表
-- ============================================

-- AI分析日志表
CREATE TABLE IF NOT EXISTS ai_analysis_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    analysis_type ENUM('shelf', 'scan', 'food') NOT NULL COMMENT '分析类型',
    request_data JSON COMMENT '请求数据',
    response_data JSON COMMENT '响应数据',
    status ENUM('pending', 'success', 'failed') DEFAULT 'pending' COMMENT '状态',
    error_message VARCHAR(255) COMMENT '错误信息',
    processing_time_ms INT COMMENT '处理时间(毫秒)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (analysis_type),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI分析日志表';

-- ============================================
-- 12. 初始化数据
-- ============================================

-- 插入店铺类型
INSERT INTO shop_types (name, description, icon, color) VALUES
('便利店', '24小时便利店、夫妻店', 'store', '#1890FF'),
('超市', '大型超市、购物中心', 'shopping_mall', '#722ED1'),
('面包店', '面包房、烘焙店', 'bakery', '#FA8C16'),
('水果店', '水果店、生鲜超市', 'fruit', '#52C41A'),
('奶茶店', '茶饮店、咖啡店', 'drink', '#EB2F96'),
('快餐店', '快餐店、小吃店', 'food', '#FAAD14');

-- 插入食品类型
INSERT INTO food_types (name, icon, color) VALUES
('面包', 'bread', '#FA8C16'),
('乳制品', 'milk', '#1890FF'),
('蔬菜', 'vegetable', '#52C41A'),
('水果', 'fruit', '#F5222D'),
('肉类', 'meat', '#722ED1'),
('饮料', 'drink', '#EB2F96'),
('零食', 'snack', '#FAAD14');

-- 插入积分规则
INSERT INTO point_rules (rule_type, rule_name, points, daily_limit, description) VALUES
('scan', '扫码发现', 10, 5, '发现未标注的临期食品'),
('audit_pass', '审核通过', 20, 10, '提交的扫码记录审核通过'),
('purchase', '购买临期食品', 5, 20, '每次购买获得积分'),
('challenge_complete', '完成挑战', 50, NULL, '完成环保挑战'),
('badge_unlock', '解锁徽章', 30, NULL, '解锁成就徽章'),
('invite_friend', '邀请好友', 20, 5, '成功邀请一位好友');

-- 插入示例挑战
INSERT INTO challenges (name, description, target, unit, reward_points, start_date, end_date) VALUES
('剩食猎人初阶', '成为环保小卫士', 1, 'kg', 100, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY)),
('救粮达人', '累计节省食物5kg', 5, 'kg', 200, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 60 DAY)),
('碳排放终结者', '减少碳排放10kg', 10, 'kg', 500, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 90 DAY)),
('美食探险家', '发现10种不同的临期食品', 10, '种', 150, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY)),
('连续打卡王', '连续7天使用App', 7, '天', 100, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY));

-- 插入示例徽章
INSERT INTO badges (name, description, icon, unlock_condition, reward_points) VALUES
('初出茅庐', '完成第一次购买', 'badge_1', 'purchase_count >= 1', 10),
('剩食猎人', '累计节省1kg食物', 'badge_2', 'food_saved >= 1', 20),
('环保先锋', '累计节省5kg食物', 'badge_3', 'food_saved >= 5', 50),
('碳排放克星', '减少碳排放5kg', 'badge_4', 'carbon_saved >= 5', 50),
('扫码达人', '扫码发现10次', 'badge_5', 'scan_count >= 10', 30),
('挑战王', '完成5个挑战', 'badge_6', 'challenge_complete >= 5', 100);

-- ============================================
-- 完成
-- ============================================
SELECT '数据库初始化完成！共创建 24 张表' AS status;
