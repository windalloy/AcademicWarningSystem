# 大学生学业预警与成绩分析系统

## 项目简介

这是一个基于 Python + MySQL 的大学生学业预警与成绩分析系统，提供图形化界面进行数据管理和查询分析。

## 功能特点

- ✅ 学生信息管理（增删改查）
- ✅ 课程信息管理（增删改查）
- ✅ 成绩录入与管理（自动计算GPA和学分）
- ✅ 学业预警分析（自动筛选预警学生）
- ✅ 数据统计分析（GPA排名、院系统计、学期统计等）
- ✅ 数据库自动初始化

## 系统要求

- Python 3.7 或更高版本
- MySQL 8.0 或更高版本
- Windows / Linux / macOS

## 安装步骤

### 1. 安装 MySQL

**Windows:**
- 下载并安装 MySQL: https://dev.mysql.com/downloads/mysql/
- 记住设置的 root 密码

**验证安装:**
```bash
mysql --version
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

或者直接安装：
```bash
pip install mysql-connector-python
```

### 3. 运行程序

```bash
python main.py
```

## 使用说明

### 首次使用

1. **启动程序**
   ```bash
   python main.py
   ```

2. **配置数据库连接**
   - 点击菜单 "文件" → "数据库连接"
   - 或点击工具栏 "连接数据库" 按钮
   - 输入 MySQL 连接信息：
     - 主机：localhost
     - 端口：3306
     - 用户名：root
     - 密码：您的 MySQL root 密码
     - 数据库：AcademicWarningSystem

3. **初始化数据库**
   - 点击菜单 "文件" → "初始化数据库"
   - 或点击工具栏 "初始化数据库" 按钮
   - 确认后会自动创建数据库和表，并插入测试数据

### 功能模块

#### 1. 学生管理
- 添加、修改、删除学生信息
- 查看学生列表（包括总学分和GPA）

#### 2. 课程管理
- 添加、修改、删除课程信息
- 设置课程类型（核心/通识/选修）

#### 3. 成绩管理
- 录入学生成绩
- 系统自动计算：
  - 绩点（GPA_Point）：90-100=4.0, 80-89=3.0, 70-79=2.0, 60-69=1.0, <60=0.0
  - 是否通过（≥60为通过）
  - 学生总学分和平均GPA

#### 4. 查询分析
- **预警学生名单**：自动筛选满足预警条件的学生
- **学生GPA排名**：按GPA从高到低排序
- **不及格课程**：查看核心课程不及格记录
- **学分完成情况**：查看每位学生的已获学分
- **院系统计**：各院系平均GPA和学分统计
- **学期统计**：每学期的选课和成绩统计

## 数据库说明

### 数据库结构

- **Student（学生表）**：存储学生基本信息
- **Course（课程表）**：存储课程信息
- **Score（成绩表）**：存储学生成绩记录
- **GraduationRequirement（毕业要求表）**：存储各院系毕业要求
- **CoreCourse（核心课程表）**：存储各院系核心课程清单

### 自动化机制

1. **触发器**：自动计算绩点和是否通过
2. **触发器**：自动更新学生的总学分和GPA
3. **存储过程**：自动生成预警学生名单

## 常见问题

### Q1: 连接数据库失败
**A:** 请检查：
- MySQL 服务是否启动
- 用户名和密码是否正确
- 端口号是否正确（默认3306）
- 防火墙是否阻止连接

### Q2: 初始化数据库失败
**A:** 请检查：
- MySQL 服务是否正常运行
- root 用户是否有创建数据库的权限
- SQL 文件路径是否正确

### Q3: 中文显示乱码
**A:** 确保数据库使用 utf8mb4 字符集（脚本中已设置）

### Q4: 如何修改数据库连接信息
**A:** 点击菜单 "文件" → "数据库连接" 重新配置

## 技术栈

- **后端**：Python 3.x
- **数据库**：MySQL 8.0
- **GUI框架**：Tkinter
- **数据库驱动**：mysql-connector-python

## 文件结构

```
gradeanal/
├── main.py                          # 主程序入口
├── AcademicWarningSystem.sql       # 数据库初始化脚本
├── requirements.txt                 # Python依赖
├── README.md                        # 说明文档
├── MySQL使用说明.md                 # MySQL使用说明
├── database/
│   └── db_manager.py                # 数据库管理模块
└── gui/
    ├── main_window.py               # 主窗口
    ├── connection_dialog.py        # 连接对话框
    ├── student_management.py       # 学生管理界面
    ├── course_management.py         # 课程管理界面
    ├── score_management.py          # 成绩管理界面
    └── query_frame.py               # 查询分析界面
```

## 开发说明

### 添加新功能

1. 在 `database/db_manager.py` 中添加数据库操作方法
2. 在相应的 GUI 模块中添加界面控件
3. 连接界面和数据库操作

### 数据库操作示例

```python
from database.db_manager import DatabaseManager

db = DatabaseManager()
db.set_config('localhost', 3306, 'root', 'password', 'AcademicWarningSystem')
if db.connect():
    # 查询所有学生
    students = db.get_all_students()
    print(students)
    db.disconnect()
```

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件

---

**祝您使用愉快！** 🎓

