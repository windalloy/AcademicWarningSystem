# 大学生学业预警与成绩分析系统 - ER图

## 实体关系图（ER Diagram）

```mermaid
erDiagram
    %% 核心实体：成绩表（放在中心位置）
    Score {
        VARCHAR SNo PK_FK "学号"
        VARCHAR CNo PK_FK "课程号"
        VARCHAR Semester PK "学期"
        DECIMAL ScoreValue "成绩"
    }
    
    %% 主要实体
    Student {
        VARCHAR SNo PK "学号"
        VARCHAR SName "姓名"
        VARCHAR Dept "院系"
        INT EnrollmentYear "入学年份"
    }
    
    Course {
        VARCHAR CNo PK "课程号"
        VARCHAR CName "课程名"
        DECIMAL Credit "学分"
        ENUM CourseType "课程类型"
    }
    
    %% 配置实体
    GraduationRequirement {
        INT ReqID PK "要求ID"
        VARCHAR Dept UK "适用院系"
        DECIMAL TotalCreditRequired "总学分要求"
        INT CoreCourseFailLimit "核心课不及格上限"
        DECIMAL MinGPA "最低GPA要求"
    }
    
    CoreCourse {
        VARCHAR Dept PK_FK "院系"
        VARCHAR CNo PK_FK "课程号"
    }
    
    %% 关系定义：使用简短清晰的标签
    Student ||--o{ Score : "选课"
    Course ||--o{ Score : "被选"
    Student }o--|| GraduationRequirement : "属于"
    Course ||--o{ CoreCourse : "核心课程"
    GraduationRequirement ||--o{ CoreCourse : "院系配置"
```

## 实体说明

### 1. Student（学生）
- **主键**：SNo（学号）
- **属性**：姓名、院系、入学年份
- **关系**：
  - 一对多：一个学生可以有多条成绩记录（Score）
  - 多对一：多个学生属于一个院系，对应一个毕业要求（GraduationRequirement）

### 2. Course（课程）
- **主键**：CNo（课程号）
- **属性**：课程名、学分、课程类型
- **关系**：
  - 一对多：一门课程可以有多条成绩记录（Score）
  - 一对多：一门课程可以是多个院系的核心课程（CoreCourse）

### 3. Score（成绩）
- **主键**：(SNo, CNo, Semester) - 联合主键
- **属性**：成绩
- **外键**：
  - SNo → Student.SNo
  - CNo → Course.CNo
- **关系**：
  - 多对一：多条成绩记录属于一个学生
  - 多对一：多条成绩记录属于一门课程

### 4. GraduationRequirement（毕业要求）
- **主键**：ReqID（要求ID）
- **唯一键**：Dept（院系）
- **属性**：总学分要求、核心课不及格上限、最低GPA要求
- **关系**：
  - 一对多：一个毕业要求对应多个学生（通过院系关联）

### 5. CoreCourse（核心课程）
- **主键**：(Dept, CNo) - 联合主键
- **外键**：
  - CNo → Course.CNo
- **关系**：
  - 多对一：多个核心课程记录属于一门课程
  - 多对一：多个核心课程记录属于一个院系（通过Dept关联）

## 关系说明

1. **Student - Score**：一对多
   - 一个学生可以有多条成绩记录
   - 级联删除：删除学生时，自动删除其所有成绩记录

2. **Course - Score**：一对多
   - 一门课程可以有多条成绩记录
   - 级联删除：删除课程时，自动删除所有相关成绩记录

3. **Student - GraduationRequirement**：多对一（通过Dept关联）
   - 多个学生属于一个院系
   - 一个院系有一个毕业要求

4. **Course - CoreCourse**：一对多
   - 一门课程可以是多个院系的核心课程
   - 级联删除：删除课程时，自动删除所有相关核心课程记录

5. **Student - CoreCourse**：多对一（通过Dept关联）
   - 多个学生属于一个院系
   - 一个院系有多门核心课程

## 约束说明

- **外键约束**：所有外键都设置了 `ON DELETE CASCADE`，保证数据一致性
- **唯一约束**：GraduationRequirement.Dept 设置为 UNIQUE，确保每个院系只有一个毕业要求
- **检查约束**：Score.ScoreValue 限制在 0-100 之间，Course.Credit 必须大于 0

## 设计特点

1. **严格遵循三大范式**：无冗余字段
2. **级联删除**：保证数据完整性
3. **联合主键**：Score 和 CoreCourse 使用联合主键，支持同一学生同一课程多次选课（不同学期）
4. **索引优化**：在常用查询字段上建立索引，提高查询性能

## 使用提示

**如果关系标签显示过小或被遮挡，建议：**

1. **在线Mermaid编辑器**：访问 https://mermaid.live/ 或 https://mermaid.ink/ 查看和导出
2. **导出为SVG/PNG**：在支持Mermaid的编辑器中导出为图片，然后放大查看
3. **调整浏览器缩放**：在Markdown预览中按 `Ctrl + 滚轮` 放大查看
4. **使用专业工具**：如Draw.io、Lucidchart等工具重新绘制，可以完全控制字体大小和布局

**关系说明（如标签看不清可参考）：**
- Student → Score：选课（1对多）
- Course → Score：被选（1对多）
- Student → GraduationRequirement：属于院系（多对1）
- Course → CoreCourse：核心课程（1对多）
- GraduationRequirement → CoreCourse：院系配置（1对多）

