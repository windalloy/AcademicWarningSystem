# 大学生学业预警与成绩分析系统 - ER图（文本版）

## 实体关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                        实体关系图（ER Diagram）                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│    Student      │ 学生
│─────────────────│
│ SNo (PK)        │ 学号
│ SName           │ 姓名
│ Dept            │ 院系
│ EnrollmentYear  │ 入学年份
└────────┬────────┘
         │
         │ 1
         │
         │ 选课
         │
         │ N
         ▼
┌─────────────────┐
│     Score       │ 成绩
│─────────────────│
│ SNo (PK,FK)     │ 学号
│ CNo (PK,FK)     │ 课程号
│ Semester (PK)   │ 学期
│ ScoreValue      │ 成绩
└────────┬────────┘
         │
         │ N
         │
         │ 被选
         │
         │ 1
         ▼
┌─────────────────┐
│     Course      │ 课程
│─────────────────│
│ CNo (PK)        │ 课程号
│ CName           │ 课程名
│ Credit          │ 学分
│ CourseType      │ 课程类型
└────────┬────────┘
         │
         │ 1
         │
         │ 是核心课程
         │
         │ N
         ▼
┌─────────────────┐
│   CoreCourse    │ 核心课程
│─────────────────│
│ Dept (PK)       │ 院系
│ CNo (PK,FK)     │ 课程号
└─────────────────┘

┌─────────────────┐
│ GraduationReq   │ 毕业要求
│─────────────────│
│ ReqID (PK)      │ 要求ID
│ Dept (UK)       │ 适用院系（唯一）
│ TotalCreditReq  │ 总学分要求
│ CoreFailLimit   │ 核心课不及格上限
│ MinGPA          │ 最低GPA要求
└─────────────────┘

关系说明：
Student (1) ──────< (N) Score         一对多：一个学生有多条成绩记录
Course (1) ──────< (N) Score          一对多：一门课程有多条成绩记录
Course (1) ──────< (N) CoreCourse      一对多：一门课程可以是多个院系的核心课程
Student.Dept = GraduationRequirement.Dept  多对一：多个学生对应一个毕业要求（通过院系）
Student.Dept = CoreCourse.Dept            多对一：多个学生对应多门核心课程（通过院系）
```

## 详细实体说明

### 实体1：Student（学生）

**属性**：
- SNo（学号）- 主键，VARCHAR(20)
- SName（姓名）- VARCHAR(50)，非空
- Dept（院系）- VARCHAR(50)，非空
- EnrollmentYear（入学年份）- INT，非空

**关系**：
- 与 Score：一对多（1:N）
  - 一个学生可以有多条成绩记录
  - 外键：Score.SNo → Student.SNo
  - 级联删除：删除学生时，自动删除其所有成绩记录

- 与 GraduationRequirement：多对一（N:1）
  - 通过 Dept 字段关联
  - 多个学生属于一个院系，对应一个毕业要求

- 与 CoreCourse：多对一（N:1）
  - 通过 Dept 字段关联
  - 多个学生属于一个院系，该院系有多门核心课程

---

### 实体2：Course（课程）

**属性**：
- CNo（课程号）- 主键，VARCHAR(20)
- CName（课程名）- VARCHAR(100)，非空
- Credit（学分）- DECIMAL(3,1)，非空，> 0
- CourseType（课程类型）- ENUM('核心', '通识', '选修')，非空

**关系**：
- 与 Score：一对多（1:N）
  - 一门课程可以有多条成绩记录
  - 外键：Score.CNo → Course.CNo
  - 级联删除：删除课程时，自动删除所有相关成绩记录

- 与 CoreCourse：一对多（1:N）
  - 一门课程可以是多个院系的核心课程
  - 外键：CoreCourse.CNo → Course.CNo
  - 级联删除：删除课程时，自动删除所有相关核心课程记录

---

### 实体3：Score（成绩）

**属性**：
- SNo（学号）- 主键的一部分，外键，VARCHAR(20)
- CNo（课程号）- 主键的一部分，外键，VARCHAR(20)
- Semester（学期）- 主键的一部分，VARCHAR(20)，非空
- ScoreValue（成绩）- DECIMAL(5,2)，非空，0-100

**主键**：(SNo, CNo, Semester) - 联合主键
- 支持同一学生同一课程在不同学期多次选课

**关系**：
- 与 Student：多对一（N:1）
  - 多条成绩记录属于一个学生
  - 外键：Score.SNo → Student.SNo

- 与 Course：多对一（N:1）
  - 多条成绩记录属于一门课程
  - 外键：Score.CNo → Course.CNo

---

### 实体4：GraduationRequirement（毕业要求）

**属性**：
- ReqID（要求ID）- 主键，INT，自增
- Dept（适用院系）- VARCHAR(50)，非空，唯一
- TotalCreditRequired（总学分要求）- DECIMAL(5,2)，非空，> 0
- CoreCourseFailLimit（核心课不及格数量上限）- INT，非空，≥ 0
- MinGPA（最低GPA要求）- DECIMAL(3,2)，非空，0-4

**关系**：
- 与 Student：一对多（1:N）
  - 通过 Dept 字段关联
  - 一个院系有一个毕业要求，对应多个学生

---

### 实体5：CoreCourse（核心课程）

**属性**：
- Dept（院系）- 主键的一部分，VARCHAR(50)，非空
- CNo（课程号）- 主键的一部分，外键，VARCHAR(20)，非空

**主键**：(Dept, CNo) - 联合主键
- 表示某个院系的某门核心课程

**关系**：
- 与 Course：多对一（N:1）
  - 多个核心课程记录属于一门课程
  - 外键：CoreCourse.CNo → Course.CNo

- 与 Student：多对一（N:1）
  - 通过 Dept 字段关联
  - 一个院系有多门核心课程，对应多个学生

---

## 关系汇总表

| 实体1 | 关系类型 | 实体2 | 说明 | 外键 |
|-------|---------|-------|------|------|
| Student | 1:N | Score | 一个学生有多条成绩记录 | Score.SNo → Student.SNo |
| Course | 1:N | Score | 一门课程有多条成绩记录 | Score.CNo → Course.CNo |
| Course | 1:N | CoreCourse | 一门课程可以是多个院系的核心课程 | CoreCourse.CNo → Course.CNo |
| Student | N:1 | GraduationRequirement | 多个学生对应一个毕业要求（通过Dept） | Student.Dept = GraduationRequirement.Dept |
| Student | N:1 | CoreCourse | 多个学生对应多门核心课程（通过Dept） | Student.Dept = CoreCourse.Dept |

## 约束说明

### 主键约束
- Student: SNo
- Course: CNo
- Score: (SNo, CNo, Semester) - 联合主键
- GraduationRequirement: ReqID
- CoreCourse: (Dept, CNo) - 联合主键

### 外键约束
- Score.SNo → Student.SNo (ON DELETE CASCADE)
- Score.CNo → Course.CNo (ON DELETE CASCADE)
- CoreCourse.CNo → Course.CNo (ON DELETE CASCADE)

### 唯一约束
- GraduationRequirement.Dept (UNIQUE)

### 检查约束
- Score.ScoreValue: 0 ≤ ScoreValue ≤ 100
- Course.Credit: Credit > 0
- GraduationRequirement.TotalCreditRequired: > 0
- GraduationRequirement.CoreCourseFailLimit: ≥ 0
- GraduationRequirement.MinGPA: 0 ≤ MinGPA ≤ 4

## 设计特点

1. **严格遵循三大范式**：无冗余字段，所有计算值通过视图和函数动态获取
2. **级联删除**：保证数据完整性，删除主表记录时自动删除相关从表记录
3. **联合主键**：Score 和 CoreCourse 使用联合主键，支持复杂业务场景
4. **索引优化**：在常用查询字段上建立索引，提高查询性能

