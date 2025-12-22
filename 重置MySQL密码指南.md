# MySQL 密码重置指南

## ⚠️ 重要说明

**运行 `python main.py` 之前：**
1. ✅ MySQL 必须**已安装**
2. ✅ MySQL **服务必须正在运行**（不仅仅是安装）
3. ✅ 需要知道 root 密码（如果忘记，需要重置）

**简单理解：**
- MySQL 就像一台服务器，需要**启动服务**才能连接
- 就像打开电脑后，需要启动程序才能使用

---

## 第一步：检查 MySQL 服务是否运行

### 方法1：使用检查脚本（推荐）

双击运行：**`检查MySQL服务.bat`**

### 方法2：手动检查

1. 按 `Win + R`，输入 `services.msc`，回车
2. 查找 "MySQL" 或 "MySQL80" 服务
3. 查看状态：
   - **正在运行** ✅ → 可以继续
   - **已停止** ❌ → 需要启动（右键 → 启动）

### 方法3：命令行检查

打开命令提示符（管理员），输入：
```bash
sc query MySQL80
```
或
```bash
sc query MySQL
```

如果显示 `STATE: 4 RUNNING`，说明服务正在运行。

---

## 第二步：重置 MySQL 密码

### 方法一：使用 MySQL Installer（最简单）⭐ 推荐

**适合：通过 MySQL Installer 安装的用户**

1. **打开 MySQL Installer**
   - 在开始菜单搜索 "MySQL Installer"
   - 或找到：`C:\Program Files\MySQL\MySQL Installer for Windows`

2. **选择 "Reconfigure"（重新配置）**
   - 在已安装产品列表中找到 MySQL Server
   - 点击右侧的 "Reconfigure" 按钮

3. **在配置向导中**
   - 一直点击 "Next" 直到 "Accounts and Roles" 页面
   - 在 "Root Account Password" 输入框中设置**新密码**
   - **请记住这个新密码！**（建议写在纸上）
   - 继续完成配置

4. **完成**
   - 配置完成后，MySQL 服务会自动重启
   - 使用新设置的密码连接

---

### 方法二：通过命令行重置（适合高级用户）

**如果方法一不行，使用这个方法**

#### 步骤1：停止 MySQL 服务

**以管理员身份**打开命令提示符（PowerShell），执行：

```powershell
net stop MySQL80
```
或
```powershell
net stop MySQL
```

#### 步骤2：以跳过权限表方式启动 MySQL

打开**新的**命令提示符窗口（以管理员身份），执行：

```bash
cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
mysqld --console --skip-grant-tables --shared-memory
```

**⚠️ 重要：这个窗口要保持打开，不要关闭！**

#### 步骤3：重置密码（新开一个命令提示符窗口）

打开**另一个**命令提示符窗口（不需要管理员），执行：

```bash
cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
mysql -u root
```

然后在 MySQL 命令行中执行：

```sql
USE mysql;
ALTER USER 'root'@'localhost' IDENTIFIED BY '您的新密码';
FLUSH PRIVILEGES;
EXIT;
```

**⚠️ 将 "您的新密码" 替换为您想设置的实际密码！**

#### 步骤4：重启 MySQL 服务

1. 关闭步骤2中打开的 mysqld 窗口（按 `Ctrl+C`）
2. 在服务管理器中启动 MySQL 服务
   或使用命令：
```powershell
net start MySQL80
```

---

## 第三步：测试新密码

### 使用命令行测试

打开命令提示符，执行：

```bash
mysql -u root -p
```

输入新设置的密码，如果成功进入 MySQL 命令行（显示 `mysql>`），说明密码正确。

### 使用 Python 测试

运行程序后，在连接对话框中：
1. 输入新设置的密码
2. 点击"测试连接"
3. 如果成功，说明密码正确

---

## 常见问题

### Q1：找不到 MySQL Installer

**解决方法：**
- 可能未通过 Installer 安装
- 使用命令行方法重置密码
- 或重新下载 MySQL Installer

### Q2：MySQL 服务无法启动

**可能原因：**
- 端口被占用
- 配置文件错误
- 权限问题

**解决方法：**
- 检查错误日志
- 或重新安装 MySQL

### Q3：重置密码后还是连接不上

**检查清单：**
- [ ] MySQL 服务是否运行？
- [ ] 密码是否正确？（注意大小写）
- [ ] 用户名是否为 `root`？
- [ ] 端口是否为 `3306`？

---

## 快速操作流程

```
1. 检查服务 → 运行 "检查MySQL服务.bat"
   ↓
2. 如果服务未运行 → 启动服务
   ↓
3. 如果忘记密码 → 使用 MySQL Installer 重置
   ↓
4. 测试连接 → 使用新密码连接
   ↓
5. 运行程序 → python main.py
```

---

## 重要提示

1. **记住新密码**：重置后，请将密码记录在安全的地方
2. **服务必须运行**：每次使用前确保 MySQL 服务正在运行
3. **首次使用**：连接成功后，记得点击"初始化数据库"

---

**如果以上方法都不行，可以考虑重新安装 MySQL（在安装时设置密码并记住）**

