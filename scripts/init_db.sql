CREATE DATABASE IF NOT EXISTS ugcData DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ugcData;

CREATE TABLE products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(2048) NOT NULL COMMENT '商品标题',
    price DECIMAL(10, 2) NOT NULL COMMENT '商品价格',
    image_url TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '商品图片URL',
    product_url TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '商品链接',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE content_generation_requests (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT NOT NULL COMMENT '关联的商品ID',
    style VARCHAR(100) NOT NULL COMMENT '文案风格',
    length VARCHAR(50) NOT NULL COMMENT '文案长度',
    language VARCHAR(50) NOT NULL COMMENT '文案语言',
    content TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '生成的文案内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 