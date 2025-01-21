# UGC-Back-End-Python

环境配置：

创建 pythonh 环境，使用 uv 替代 pip

具体已写好脚本


创建表：


根据需求选择合适的 `TEXT` 类型：

- TINYTEXT：最多 255 字节。
- TEXT：最多 65,535 字节。
- MEDIUMTEXT：最多 16 MB。
- LONGTEXT：最多 4 GB。

示例修改：

```sql

CREATETABLEproducts (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    title VARCHAR(2048) NOT NULL COMMENT '商品标题',

    price DECIMAL(10, 2) NOT NULL COMMENT '商品价格',

    image_url TEXTDEFAULTNULL COMMENT '商品图片URL',

    product_url TEXTNOT NULL COMMENT '商品链接',

    created_at TIMESTAMPDEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    updated_at TIMESTAMPDEFAULT CURRENT_TIMESTAMP ONUPDATE CURRENT_TIMESTAMP COMMENT '更新时间'

);

```



### 4. 进入 MySQL 容器

你可以通过以下命令进入容器：

```bash

dockerexec-itmysql-containermysql-uroot-p

```

输入你设置的  后，即可进入 MySQL 控制台。


```bash
  
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=your_password -d -p 3306:3306 \
-v /path/to/your/data:/var/lib/mysql mysql:8.0  //替换挂载数据路径
```
