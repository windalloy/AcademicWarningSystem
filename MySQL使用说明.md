# MySQL 数据库使用说明

## 一、安装 MySQL

### Windows 系统
1. 下载 MySQL 安装包：https://dev.mysql.com/downloads/mysql/
2. 运行安装程序，选择 "Developer Default" 或 "Server only"
3. 设置 root 用户密码（请记住这个密码）
4. 完成安装

### 验证安装
打开命令提示符（CMD）或 PowerShell，输入：
```bash
mysql --version
```

## 二、执行 SQL 脚本

### 方法1：使用命令行（推荐）

1. **打开命令提示符或 PowerShell**

2. **登录 MySQL**（需要输入root密码）
```bash
mysql -u root -p
```

3. **执行 SQL 脚本**
```bash
source D:/py/gradeanal/AcademicWarningSystem.sql
```
或者：
```bash
mysql -u root -p < D:/py/gradeanal/AcademicWarningSystem.sql
```

### 方法2：使用 MySQL Workbench（图形界面）

1. **下载并安装 MySQL Workbench**
   - 下载地址：https://dev.mysql.com/downloads/workbench/

2. **连接到 MySQL 服务器**
   - 打开 MySQL Workbench
   - 点击 "Local instance MySQL" 或创建新连接
   - 输入 root 密码

3. **执行 SQL 脚本**
   - 点击菜单：File → Open SQL Script
   - 选择 `AcademicWarningSystem.sql` 文件
   - 点击执行按钮（⚡图标）或按 `Ctrl+Shift+Enter`

### 方法3：使用 Python 脚本自动执行

我已经创建了一个 Python GUI 应用，它会自动处理数据库初始化。

## 三、验证数据库创建成功

登录 MySQL 后，执行以下命令：

```sql
-- 查看数据库
SHOW DATABASES;

-- 使用数据库
USE AcademicWarningSystem;

-- 查看所有表
SHOW TABLES;

-- 查看学生表数据
SELECT * FROM Student LIMIT 5;

-- 测试预警存储过程
CALL usp_GenerateWarningList();
```

## 四、常见问题

### 问题1：找不到 mysql 命令
**解决方案**：将 MySQL 的 bin 目录添加到系统环境变量 PATH 中
- 默认路径：`C:\Program Files\MySQL\MySQL Server 8.0\bin`

### 问题2：Access denied for user 'root'@'localhost'
**解决方案**：
- 检查密码是否正确
- 如果忘记密码，需要重置 MySQL root 密码

### 问题3：中文乱码
**解决方案**：确保数据库使用 utf8mb4 字符集（脚本中已设置）

## 五、数据库连接信息

使用 Python GUI 应用或编写程序时，需要以下信息：
- **主机**：localhost 或 127.0.0.1
- **端口**：3306（MySQL 默认端口）
- **用户名**：root（或您创建的其他用户）
- **密码**：您设置的 MySQL root 密码
- **数据库名**：AcademicWarningSystem

