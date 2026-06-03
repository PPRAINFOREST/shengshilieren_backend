# 达梦数据库 vs MySQL 语法区别

本文档整理了达梦数据库（DM8）与 MySQL 在语法上的主要区别，供开发参考。

---

## 1. 布尔/位类型

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `TRUE` / `FALSE` | `1` / `0` | 达梦不支持 TRUE/FALSE 关键字 |
| `BOOLEAN` | `TINYINT` | 达梦无 BOOLEAN 类型 |
| `BIT(1)` | `TINYINT` | 位类型不同 |

### 示例

```sql
-- MySQL
CREATE TABLE t (
    is_active BOOLEAN DEFAULT TRUE,
    verified BIT(1) DEFAULT 0
);

-- 达梦
CREATE TABLE t (
    is_active TINYINT DEFAULT 1,
    verified TINYINT DEFAULT 0
);
```

---

## 2. 自增主键与序列

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `AUTO_INCREMENT` | 序列 `SEQUENCE` | 达梦需要手动创建序列 |
| 插入时自动递增 | 需要 `序列.NEXTVAL` | 达梦需显式调用 |

### 示例

```sql
-- MySQL
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50)
);
INSERT INTO users VALUES (NULL, '张三');  -- 自动生成 ID

-- 达梦
CREATE SEQUENCE users_seq START WITH 1 INCREMENT BY 1;

CREATE TABLE users (
    id INT DEFAULT users_seq.NEXTVAL PRIMARY KEY,
    name VARCHAR(50)
);
INSERT INTO users VALUES (users_seq.NEXTVAL, '张三');
```

### 序列操作

```sql
-- 创建序列
CREATE SEQUENCE seq_name START WITH 1 INCREMENT BY 1 NOMAXVALUE NOCYCLE;

-- 获取下一个值
SELECT seq_name.NEXTVAL FROM DUAL;

-- 获取当前值
SELECT seq_name.CURRVAL FROM DUAL;

-- 重置序列
ALTER SEQUENCE seq_name RESTART WITH 1;

-- 删除序列
DROP SEQUENCE seq_name;
```

---

## 3. 外键检查

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `SET FOREIGN_KEY_CHECKS = 0` | `SET FOREIGN_KEY_CHECKS = 0` | ✅ 语法相同 |
| `SET REFERENTIAL_INTEGRITY FALSE` | ❌ 不支持 | 达梦无此语法 |

---

## 4. 字符串类型

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `VARCHAR(255)` | `VARCHAR2(255)` 或 `VARCHAR(255)` | 达梦优先用 VARCHAR2 |
| `TEXT` | `CLOB` 或 `TEXT` | 两者都支持 |
| `CHAR` | `CHAR` | ✅ 相同 |
| `utf8mb4` | `UTF8` | 字符集名称不同 |
| `utf8mb4_unicode_ci` | `UTF8_UNICODE_LE` | 排序规则不同 |

### 示例

```sql
-- MySQL
CREATE TABLE t (
    name VARCHAR(100) CHARACTER SET utf8mb4,
    bio TEXT CHARACTER SET utf8mb4
);

-- 达梦
CREATE TABLE t (
    name VARCHAR2(100),
    bio CLOB
);
```

---

## 5. 日期时间

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `NOW()` | `SYSDATE` | 获取当前时间 |
| `CURRENT_TIMESTAMP` | `SYSDATE` | 时间戳 |
| `DATE_FORMAT(date, '%Y-%m-%d')` | `TO_CHAR(date, 'YYYY-MM-DD')` | 日期格式化 |
| `STR_TO_DATE(str, format)` | `TO_DATE(str, format)` | 字符串转日期 |

### 示例

```sql
-- MySQL
SELECT NOW(), DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s');

-- 达梦
SELECT SYSDATE, TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS');
```

---

## 6. 字符串函数

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `CONCAT(str1, str2)` | `CONCAT(str1, str2)` | ✅ 相同 |
| `SUBSTRING(str, 1, 10)` | `SUBSTR(str, 1, 10)` | 名称不同 |
| `LENGTH(str)` | `LENGTH(str)` | 相同 |
| `CHAR_LENGTH(str)` | `LENGTH(str)` (按字符) | 注意区分 |
| `GROUP_CONCAT(col)` | `LISTAGG(col, ',')` | 聚合连接 |
| `FIND_IN_SET(str, set)` | 无直接对应 | 需用 INSTR 或 LIKE |

### 示例

```sql
-- MySQL
SELECT GROUP_CONCAT(name SEPARATOR ',') FROM users;

-- 达梦
SELECT LISTAGG(name, ',') FROM users;
```

---

## 7. 空值处理

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `IFNULL(col, default)` | `NVL(col, default)` | 达梦用 NVL |
| `COALESCE(...)` | `COALESCE(...)` | ✅ 相同 |

---

## 8. 分页

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `LIMIT 10, 20` | `LIMIT 20 OFFSET 10` | 偏移量位置不同 |
| `LIMIT 10` | `LIMIT 10` | ✅ 相同 |

### 示例

```sql
-- MySQL: 跳过前10条，取10条
SELECT * FROM users LIMIT 10 OFFSET 10;
-- 或
SELECT * FROM users LIMIT 10, 10;

-- 达梦
SELECT * FROM users LIMIT 10 OFFSET 10;
```

---

## 9. 条件判断

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `IF(condition, true, false)` | `DECODE(condition, 1, true, false)` 或 `CASE WHEN` | 达梦优先用 DECODE |
| `IFNULL(...)` | `NVL(...)` | 见空值处理 |
| `NULLIF(a, b)` | `NULLIF(a, b)` | ✅ 相同 |

### 示例

```sql
-- MySQL
SELECT IF(points > 100, 'VIP', '普通') FROM customers;

-- 达梦
SELECT DECODE(SIGN(points - 100), 1, 'VIP', '普通') FROM customers;
-- 或
SELECT CASE WHEN points > 100 THEN 'VIP' ELSE '普通' END FROM customers;
```

---

## 10. 变量

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `SET @var = 1` | `DEFINE var = 1` | 会话变量 |
| `SET @var = (SELECT ...)` | `SELECT ... INTO :var` | SELECT 赋值 |

---

## 11. 存储过程

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `DELIMITER $$` | 无需定界符 | 达梦用 `CREATE PROCEDURE` |
| `END$$` | `END;` | 结束符不同 |

### 示例

```sql
-- MySQL
DELIMITER $$
CREATE PROCEDURE get_user(IN user_id INT)
BEGIN
    SELECT * FROM users WHERE id = user_id;
END$$
DELIMITER ;

-- 达梦
CREATE PROCEDURE get_user(IN user_id INT)
AS
BEGIN
    SELECT * FROM users WHERE id = user_id;
END;
```

---

## 12. 触发器

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `NEW.col` | `:NEW.col` | 达梦需加冒号 |
| `OLD.col` | `:OLD.col` | 达梦需加冒号 |

### 示例

```sql
-- MySQL
CREATE TRIGGER before_insert_user
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    SET NEW.created_at = NOW();
END;

-- 达梦
CREATE OR REPLACE TRIGGER before_insert_user
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    :NEW.created_at := SYSDATE;
END;
```

---

## 13. 注释

| MySQL | 达梦 | 说明 |
|-------|------|------|
| `-- 注释` | `-- 注释` | ✅ 相同 |
| `# 注释` | ❌ 不支持 | 达梦不支持 `#` |
| `/* 注释 */` | `/* 注释 */` | ✅ 相同 |

---

## 14. 常用 SQL 转换规则

### Python 脚本转换示例

```python
import re

def transform_mysql_to_dameng(sql: str) -> str:
    """将 MySQL SQL 转换为达梦兼容格式"""
    
    transforms = [
        # 布尔值
        (r'\bTRUE\b', '1'),
        (r'\bFALSE\b', '0'),
        
        # 引擎和字符集
        (r'\bENGINE\s*=\s*InnoDB\b', ''),
        (r'\bENGINE\s*=\s*MyISAM\b', ''),
        (r'\bCHARACTER\s+SET\s+utf8mb4\b', ''),
        (r'\bCOLLATE\s+utf8mb4_[^\s]+\b', ''),
        (r'\butf8mb4\b', 'UTF8'),
        
        # DEFINER
        (r'\bDEFINER\s*=\s*[^\s]+\b', ''),
        
        # 无符号
        (r'\bunsigned\b', ''),
        
        # 自增（需配合序列使用）
        (r'\bAUTO_INCREMENT\s*=\s*\d+', ''),
    ]
    
    result = sql
    for pattern, replacement in transforms:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result
```

---

## 15. 达梦特殊配置

### 兼容 MySQL 模式

```sql
-- 启用 MySQL 兼容模式
SP_SET_PARA_VALUE(1, 'COMPATIBLE_MODE', 4);

-- 关闭密码复杂度检查（开发环境）
SP_SET_PARA_VALUE(1, 'PWD_POLICY', 0);

-- 控制 NULL 值排序位置（MySQL 行为）
SP_SET_PARA_VALUE(1, 'ORDER_BY_NULLS_FLAG', 2);
```

### 查看参数

```sql
-- 查看当前参数
SELECT * FROM V$PARAMETER WHERE NAME LIKE '%COMPATIBLE%';

-- 查看版本信息
SELECT * FROM V$VERSION;
```

---

## 16. 快速参考表

| 场景 | MySQL | 达梦 |
|------|-------|------|
| 当前时间 | `NOW()` | `SYSDATE` |
| 空值处理 | `IFNULL(a,b)` | `NVL(a,b)` |
| 字符串截取 | `SUBSTRING()` | `SUBSTR()` |
| 布尔真值 | `TRUE` | `1` |
| 自增主键 | `AUTO_INCREMENT` | `SEQUENCE.NEXTVAL` |
| 分页 | `LIMIT n, m` | `LIMIT m OFFSET n` |
| 注释单行 | `--` 或 `#` | `--` |
| 触发器引用 | `NEW.col` | `:NEW.col` |
| 字符集 | `utf8mb4` | `UTF8` |
| 外键检查 | `FOREIGN_KEY_CHECKS` | `FOREIGN_KEY_CHECKS` ✅ |

---

## 17. 迁移检查清单

- [ ] 将 `TRUE`/`FALSE` 替换为 `1`/`0`
- [ ] 将 `AUTO_INCREMENT` 替换为 `SEQUENCE`
- [ ] 将 `NOW()` 替换为 `SYSDATE`
- [ ] 将 `IFNULL` 替换为 `NVL`
- [ ] 将 `SUBSTRING` 替换为 `SUBSTR`
- [ ] 将 `ENGINE=InnoDB` 删除
- [ ] 将 `CHARACTER SET utf8mb4` 替换为 `UTF8`
- [ ] 触发器中 `NEW`/`OLD` 加上 `:`
- [ ] 移除 `#` 开头的注释
- [ ] 检查序列是否正确创建

---

## 18. 参考资料

- [达梦官方文档](https://eco.dameng.com/document/dm/zh-cn/)
- [MySQL 到 DM 移植指南](https://eco.dameng.com/document/dm/zh-cn/start/mysql_dm.html)
- [达梦 DTS 迁移工具](https://eco.dameng.com/document/dm/zh-cn/start/tool-dm-migrate.html)
