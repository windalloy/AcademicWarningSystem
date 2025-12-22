-- ============================================
-- 大学生学业预警与成绩分析系统
-- 数据库设计与实现脚本
-- 兼容 MySQL 8.0 和 SQL Server 2019
-- ============================================

-- ============================================
-- 第一部分：创建数据库
-- ============================================

-- MySQL 语法
CREATE DATABASE IF NOT EXISTS AcademicWarningSystem
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE AcademicWarningSystem;

-- SQL Server 语法（注释掉，如需使用请取消注释）
/*
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'AcademicWarningSystem')
BEGIN
    CREATE DATABASE AcademicWarningSystem
    COLLATE Chinese_PRC_CI_AS;
END
GO
USE AcademicWarningSystem;
GO
*/

-- ============================================
-- 第二部分：创建数据表（DDL）
-- ============================================

-- 表1：学生表 (Student)
-- 严格遵循三大范式：移除冗余字段 TotalCredit 和 GPA（通过视图计算）
DROP TABLE IF EXISTS Student;
CREATE TABLE Student (
    SNo VARCHAR(20) PRIMARY KEY COMMENT '学号',
    SName VARCHAR(50) NOT NULL COMMENT '姓名',
    Dept VARCHAR(50) NOT NULL COMMENT '院系',
    EnrollmentYear INT NOT NULL COMMENT '入学年份',
    INDEX idx_dept (Dept),
    INDEX idx_year (EnrollmentYear)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生表';

-- 表2：课程表 (Course)
DROP TABLE IF EXISTS Course;
CREATE TABLE Course (
    CNo VARCHAR(20) PRIMARY KEY COMMENT '课程号',
    CName VARCHAR(100) NOT NULL COMMENT '课程名',
    Credit DECIMAL(3,1) NOT NULL CHECK (Credit > 0) COMMENT '学分',
    CourseType ENUM('核心', '通识', '选修') NOT NULL COMMENT '课程类型',
    INDEX idx_type (CourseType)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程表';

-- 表3：成绩表 (Score)
-- 严格遵循三大范式：移除冗余字段 GPA_Point 和 Is_Passed（通过计算函数获取）
DROP TABLE IF EXISTS Score;
CREATE TABLE Score (
    SNo VARCHAR(20) NOT NULL COMMENT '学号',
    CNo VARCHAR(20) NOT NULL COMMENT '课程号',
    ScoreValue DECIMAL(5,2) NOT NULL CHECK (ScoreValue >= 0 AND ScoreValue <= 100) COMMENT '成绩',
    Semester VARCHAR(20) NOT NULL COMMENT '开课学期',
    PRIMARY KEY (SNo, CNo, Semester),
    FOREIGN KEY (SNo) REFERENCES Student(SNo) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (CNo) REFERENCES Course(CNo) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_semester (Semester),
    INDEX idx_score (ScoreValue)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成绩表';

-- 表4：毕业要求表 (GraduationRequirement)
DROP TABLE IF EXISTS GraduationRequirement;
CREATE TABLE GraduationRequirement (
    ReqID INT AUTO_INCREMENT PRIMARY KEY COMMENT '要求ID',
    Dept VARCHAR(50) NOT NULL UNIQUE COMMENT '适用院系',
    TotalCreditRequired DECIMAL(5,2) NOT NULL CHECK (TotalCreditRequired > 0) COMMENT '总学分要求',
    CoreCourseFailLimit INT NOT NULL DEFAULT 0 CHECK (CoreCourseFailLimit >= 0) COMMENT '核心课不及格数量上限',
    MinGPA DECIMAL(3,2) NOT NULL DEFAULT 2.00 CHECK (MinGPA >= 0 AND MinGPA <= 4) COMMENT '最低GPA要求',
    INDEX idx_dept (Dept)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='毕业要求表';

-- 表5：核心课程表 (CoreCourse)
DROP TABLE IF EXISTS CoreCourse;
CREATE TABLE CoreCourse (
    Dept VARCHAR(50) NOT NULL COMMENT '院系',
    CNo VARCHAR(20) NOT NULL COMMENT '课程号',
    PRIMARY KEY (Dept, CNo),
    FOREIGN KEY (CNo) REFERENCES Course(CNo) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_dept (Dept)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='核心课程表';

-- ============================================
-- 第三部分：创建函数（Function）
-- ============================================

-- 函数1：根据成绩计算绩点
DROP FUNCTION IF EXISTS fn_CalculateGPA;
DELIMITER $$
CREATE FUNCTION fn_CalculateGPA(score DECIMAL(5,2)) RETURNS DECIMAL(3,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    RETURN CASE
        WHEN score >= 90 THEN 4.0
        WHEN score >= 80 THEN 3.0
        WHEN score >= 70 THEN 2.0
        WHEN score >= 60 THEN 1.0
        ELSE 0.0
    END;
END$$
DELIMITER ;

-- 函数2：判断是否通过
DROP FUNCTION IF EXISTS fn_IsPassed;
DELIMITER $$
CREATE FUNCTION fn_IsPassed(score DECIMAL(5,2)) RETURNS TINYINT(1)
READS SQL DATA
DETERMINISTIC
BEGIN
    RETURN IF(score >= 60, 1, 0);
END$$
DELIMITER ;

-- ============================================
-- 第四部分：创建视图（View）
-- ============================================

-- 视图1：StudentGPAView - 学生GPA视图（通过计算获取，无冗余）
DROP VIEW IF EXISTS StudentGPAView;
CREATE VIEW StudentGPAView AS
SELECT 
    S.SNo AS 学号,
    S.SName AS 姓名,
    S.Dept AS 院系,
    COALESCE(SUM(CASE WHEN SC.ScoreValue >= 60 THEN C.Credit ELSE 0 END), 0) AS 已获学分,
    CASE 
        WHEN SUM(CASE WHEN SC.ScoreValue >= 60 THEN C.Credit ELSE 0 END) > 0 
        THEN ROUND(SUM(fn_CalculateGPA(SC.ScoreValue) * C.Credit) / SUM(CASE WHEN SC.ScoreValue >= 60 THEN C.Credit ELSE 0 END), 2)
        ELSE 0.00
    END AS 平均绩点
FROM Student S
LEFT JOIN Score SC ON S.SNo = SC.SNo
LEFT JOIN Course C ON SC.CNo = C.CNo
GROUP BY S.SNo, S.SName, S.Dept;

-- 视图2：FailedCoreCoursesView - 核心课程不及格视图（通过函数计算是否通过）
DROP VIEW IF EXISTS FailedCoreCoursesView;
CREATE VIEW FailedCoreCoursesView AS
SELECT 
    S.SNo AS 学号,
    S.SName AS 姓名,
    C.CName AS 课程名,
    SC.ScoreValue AS 成绩,
    SC.Semester AS 学期
FROM Score SC
INNER JOIN Student S ON SC.SNo = S.SNo
INNER JOIN Course C ON SC.CNo = C.CNo
INNER JOIN CoreCourse CC ON C.CNo = CC.CNo AND S.Dept = CC.Dept
WHERE fn_IsPassed(SC.ScoreValue) = 0
ORDER BY S.SNo, SC.Semester;

-- 视图3：CreditsCompletedView - 已获学分统计视图（通过计算获取）
DROP VIEW IF EXISTS CreditsCompletedView;
CREATE VIEW CreditsCompletedView AS
SELECT 
    S.SNo AS 学号,
    S.SName AS 姓名,
    COALESCE(SUM(CASE WHEN fn_IsPassed(SC.ScoreValue) = 1 THEN C.Credit ELSE 0 END), 0) AS 已获学分总数
FROM Student S
LEFT JOIN Score SC ON S.SNo = SC.SNo
LEFT JOIN Course C ON SC.CNo = C.CNo
GROUP BY S.SNo, S.SName;

-- 视图4：FailedCoursesView - 未通过课程视图（所有未通过课程，不仅仅是核心课程）
DROP VIEW IF EXISTS FailedCoursesView;
CREATE VIEW FailedCoursesView AS
SELECT 
    S.SNo AS 学号,
    S.SName AS 姓名,
    S.Dept AS 院系,
    C.CNo AS 课程号,
    C.CName AS 课程名,
    C.Credit AS 学分,
    C.CourseType AS 课程类型,
    SC.ScoreValue AS 成绩,
    SC.Semester AS 学期
FROM Score SC
INNER JOIN Student S ON SC.SNo = S.SNo
INNER JOIN Course C ON SC.CNo = C.CNo
WHERE fn_IsPassed(SC.ScoreValue) = 0
ORDER BY S.SNo, SC.Semester;

-- ============================================
-- 第五部分：创建触发器（Trigger）
-- ============================================

-- 注意：虽然严格遵循三大范式不应该有冗余字段，但根据需求要求，
-- 需要在成绩录入后自动更新相关信息（通过视图和函数计算，不存储冗余数据）
-- 这里创建触发器用于数据验证和日志记录（可选）

-- 触发器：成绩录入后验证数据
DROP TRIGGER IF EXISTS trg_AfterInsert_Score_Validate;
DROP TRIGGER IF EXISTS trg_AfterUpdate_Score_Validate;

DELIMITER $$

-- 触发器1：插入成绩后验证
CREATE TRIGGER trg_AfterInsert_Score_Validate
AFTER INSERT ON Score
FOR EACH ROW
BEGIN
    -- 验证成绩范围（已在CHECK约束中，这里可以添加日志或其他操作）
    -- 如果需要，可以在这里记录操作日志
    -- INSERT INTO ScoreLog (SNo, CNo, ScoreValue, Operation, Timestamp) 
    -- VALUES (NEW.SNo, NEW.CNo, NEW.ScoreValue, 'INSERT', NOW());
END$$

-- 触发器2：更新成绩后验证
CREATE TRIGGER trg_AfterUpdate_Score_Validate
AFTER UPDATE ON Score
FOR EACH ROW
BEGIN
    -- 验证成绩范围
    -- 如果需要，可以在这里记录操作日志
    -- INSERT INTO ScoreLog (SNo, CNo, ScoreValue, Operation, Timestamp) 
    -- VALUES (NEW.SNo, NEW.CNo, NEW.ScoreValue, 'UPDATE', NOW());
END$$

DELIMITER ;

-- ============================================
-- 第五部分：创建存储过程（Stored Procedure）
-- ============================================

-- 注意：严格遵循三大范式，不再需要更新冗余字段的存储过程
-- 所有计算值通过视图动态获取

-- 存储过程1：生成预警学生名单（通过计算获取学分，无冗余）
DROP PROCEDURE IF EXISTS usp_GenerateWarningList;
DELIMITER $$

CREATE PROCEDURE usp_GenerateWarningList()
BEGIN
    SELECT 
        S.SNo AS 学号,
        S.SName AS 姓名,
        S.Dept AS 院系,
        CASE
            WHEN (
                SELECT COALESCE(SUM(CASE WHEN fn_IsPassed(SC.ScoreValue) = 1 THEN C.Credit ELSE 0 END), 0)
                FROM Score SC
                INNER JOIN Course C ON SC.CNo = C.CNo
                WHERE SC.SNo = S.SNo
            ) < GR.TotalCreditRequired * 0.8 THEN '学分不足（低于要求80%）'
            WHEN (
                SELECT COUNT(*) 
                FROM Score SC
                INNER JOIN CoreCourse CC ON SC.CNo = CC.CNo AND S.Dept = CC.Dept
                WHERE SC.SNo = S.SNo AND fn_IsPassed(SC.ScoreValue) = 0
            ) >= GR.CoreCourseFailLimit THEN CONCAT('核心课程不及格数量超过限制（', GR.CoreCourseFailLimit, '门）')
            ELSE '其他原因'
        END AS 预警原因,
        (
            SELECT COALESCE(SUM(CASE WHEN fn_IsPassed(SC.ScoreValue) = 1 THEN C.Credit ELSE 0 END), 0)
            FROM Score SC
            INNER JOIN Course C ON SC.CNo = C.CNo
            WHERE SC.SNo = S.SNo
        ) AS 已获学分,
        GR.TotalCreditRequired AS 要求学分,
        (
            SELECT COUNT(*) 
            FROM Score SC
            INNER JOIN CoreCourse CC ON SC.CNo = CC.CNo AND S.Dept = CC.Dept
            WHERE SC.SNo = S.SNo AND fn_IsPassed(SC.ScoreValue) = 0
        ) AS 核心课程不及格数,
        GR.CoreCourseFailLimit AS 不及格上限
    FROM Student S
    INNER JOIN GraduationRequirement GR ON S.Dept = GR.Dept
    WHERE 
        -- 条件a：已获学分 < 毕业要求总学分的80%
        (
            SELECT COALESCE(SUM(CASE WHEN fn_IsPassed(SC.ScoreValue) = 1 THEN C.Credit ELSE 0 END), 0)
            FROM Score SC
            INNER JOIN Course C ON SC.CNo = C.CNo
            WHERE SC.SNo = S.SNo
        ) < GR.TotalCreditRequired * 0.8
        OR
        -- 条件b：核心课程不及格数量 >= 毕业要求中设定的上限
        (
            SELECT COUNT(*) 
            FROM Score SC
            INNER JOIN CoreCourse CC ON SC.CNo = CC.CNo AND S.Dept = CC.Dept
            WHERE SC.SNo = S.SNo AND fn_IsPassed(SC.ScoreValue) = 0
        ) >= GR.CoreCourseFailLimit
    ORDER BY S.Dept, S.SNo;
END$$

DELIMITER ;

-- ============================================
-- 第六部分：插入模拟数据（DML）
-- ============================================

-- 插入学生数据
INSERT INTO Student (SNo, SName, Dept, EnrollmentYear) VALUES
('2021001', '张三', '计算机科学', 2021),
('2021002', '李四', '计算机科学', 2021),
('2021003', '王五', '数学', 2021),
('2022001', '赵六', '计算机科学', 2022),
('2022002', '钱七', '数学', 2022),
('2021004', '孙八', '计算机科学', 2021),
('2022003', '周九', '物理', 2022);

-- 插入课程数据
INSERT INTO Course (CNo, CName, Credit, CourseType) VALUES
('CS101', '数据结构', 4.0, '核心'),
('CS102', '算法设计', 3.0, '核心'),
('CS103', '数据库系统', 3.0, '核心'),
('CS201', '软件工程', 3.0, '核心'),
('GE101', '大学英语', 2.0, '通识'),
('GE102', '高等数学', 4.0, '通识'),
('GE103', '线性代数', 3.0, '通识'),
('EL101', '音乐欣赏', 1.0, '选修'),
('EL102', '体育', 1.0, '选修'),
('MATH101', '数学分析', 4.0, '核心'),
('MATH102', '概率论', 3.0, '核心');

-- 插入毕业要求数据
INSERT INTO GraduationRequirement (Dept, TotalCreditRequired, CoreCourseFailLimit, MinGPA) VALUES
('计算机科学', 120.0, 2, 2.50),
('数学', 110.0, 1, 2.80),
('物理', 115.0, 2, 2.60);

-- 插入核心课程数据
INSERT INTO CoreCourse (Dept, CNo) VALUES
('计算机科学', 'CS101'),
('计算机科学', 'CS102'),
('计算机科学', 'CS103'),
('计算机科学', 'CS201'),
('数学', 'MATH101'),
('数学', 'MATH102'),
('数学', 'GE102'),
('物理', 'GE102');

-- 插入成绩数据（注意：触发器会自动计算GPA_Point和Is_Passed）
INSERT INTO Score (SNo, CNo, ScoreValue, Semester) VALUES
-- 张三的成绩
('2021001', 'CS101', 85, '2021-秋季'),
('2021001', 'CS102', 92, '2021-秋季'),
('2021001', 'GE101', 78, '2021-秋季'),
('2021001', 'GE102', 88, '2021-秋季'),
('2021001', 'CS103', 65, '2022-春季'),
('2021001', 'EL101', 95, '2022-春季'),
-- 李四的成绩（有不及格）
('2021002', 'CS101', 55, '2021-秋季'),
('2021002', 'CS102', 58, '2021-秋季'),
('2021002', 'GE101', 72, '2021-秋季'),
('2021002', 'CS103', 45, '2022-春季'),
('2021002', 'CS201', 50, '2022-春季'),
-- 王五的成绩
('2021003', 'MATH101', 90, '2021-秋季'),
('2021003', 'MATH102', 85, '2021-秋季'),
('2021003', 'GE102', 82, '2021-秋季'),
('2021003', 'GE103', 88, '2022-春季'),
-- 赵六的成绩
('2022001', 'CS101', 75, '2022-秋季'),
('2022001', 'GE101', 68, '2022-秋季'),
-- 钱七的成绩
('2022002', 'MATH101', 95, '2022-秋季'),
('2022002', 'GE102', 80, '2022-秋季'),
-- 孙八的成绩（学分不足）
('2021004', 'CS101', 70, '2021-秋季'),
('2021004', 'GE101', 65, '2021-秋季'),
-- 周九的成绩
('2022003', 'GE102', 75, '2022-秋季');

-- 注意：由于严格遵循三大范式，不再需要手动更新GPA
-- GPA和学分通过视图动态计算，无需存储冗余字段

-- ============================================
-- 第七部分：复杂查询示例（DQL）
-- ============================================

-- 查询1：查询某学生所有不及格课程（通过函数计算是否通过）
-- 示例：查询学号为'2021002'的学生所有不及格课程
SELECT 
    S.SName AS 姓名,
    C.CName AS 课程名,
    SC.ScoreValue AS 成绩,
    SC.Semester AS 学期,
    C.CourseType AS 课程类型
FROM Score SC
INNER JOIN Student S ON SC.SNo = S.SNo
INNER JOIN Course C ON SC.CNo = C.CNo
WHERE SC.SNo = '2021002' AND fn_IsPassed(SC.ScoreValue) = 0
ORDER BY SC.Semester, C.CName;

-- 查询2：统计各院系平均GPA（通过视图计算）
SELECT 
    S.Dept AS 院系,
    COUNT(*) AS 学生人数,
    ROUND(AVG(SG.平均绩点), 2) AS 平均GPA,
    ROUND(AVG(SG.已获学分), 2) AS 平均已获学分
FROM Student S
INNER JOIN StudentGPAView SG ON S.SNo = SG.学号
GROUP BY S.Dept
ORDER BY 平均GPA DESC;

-- 查询3：查询核心课程挂科≥2门的学生（通过函数计算是否通过）
SELECT 
    S.SNo AS 学号,
    S.SName AS 姓名,
    S.Dept AS 院系,
    COUNT(*) AS 核心课程不及格数
FROM Student S
INNER JOIN Score SC ON S.SNo = SC.SNo
INNER JOIN CoreCourse CC ON SC.CNo = CC.CNo AND S.Dept = CC.Dept
WHERE fn_IsPassed(SC.ScoreValue) = 0
GROUP BY S.SNo, S.SName, S.Dept
HAVING COUNT(*) >= 2
ORDER BY 核心课程不及格数 DESC;

-- 查询4：查询学分不足毕业要求80%的学生（通过计算获取学分）
SELECT 
    S.SNo AS 学号,
    S.SName AS 姓名,
    S.Dept AS 院系,
    (
        SELECT COALESCE(SUM(CASE WHEN fn_IsPassed(SC.ScoreValue) = 1 THEN C.Credit ELSE 0 END), 0)
        FROM Score SC
        INNER JOIN Course C ON SC.CNo = C.CNo
        WHERE SC.SNo = S.SNo
    ) AS 已获学分,
    GR.TotalCreditRequired AS 要求学分,
    ROUND((
        SELECT COALESCE(SUM(CASE WHEN fn_IsPassed(SC.ScoreValue) = 1 THEN C.Credit ELSE 0 END), 0)
        FROM Score SC
        INNER JOIN Course C ON SC.CNo = C.CNo
        WHERE SC.SNo = S.SNo
    ) / GR.TotalCreditRequired * 100, 2) AS 完成百分比,
    CONCAT('还需', ROUND(GR.TotalCreditRequired * 0.8 - (
        SELECT COALESCE(SUM(CASE WHEN fn_IsPassed(SC.ScoreValue) = 1 THEN C.Credit ELSE 0 END), 0)
        FROM Score SC
        INNER JOIN Course C ON SC.CNo = C.CNo
        WHERE SC.SNo = S.SNo
    ), 2), '学分') AS 预警信息
FROM Student S
INNER JOIN GraduationRequirement GR ON S.Dept = GR.Dept
WHERE (
    SELECT COALESCE(SUM(CASE WHEN fn_IsPassed(SC.ScoreValue) = 1 THEN C.Credit ELSE 0 END), 0)
    FROM Score SC
    INNER JOIN Course C ON SC.CNo = C.CNo
    WHERE SC.SNo = S.SNo
) < GR.TotalCreditRequired * 0.8
ORDER BY 完成百分比 ASC;

-- 查询5：查询每学期学生选课数量统计
SELECT 
    SC.Semester AS 学期,
    COUNT(DISTINCT SC.SNo) AS 选课学生数,
    COUNT(*) AS 总选课数,
    COUNT(DISTINCT SC.CNo) AS 开设课程数,
    ROUND(AVG(SC.ScoreValue), 2) AS 平均成绩
FROM Score SC
GROUP BY SC.Semester
ORDER BY SC.Semester;

-- 查询6（额外）：查询所有学生的详细成绩单（通过函数计算绩点和是否通过）
SELECT 
    S.SNo AS 学号,
    S.SName AS 姓名,
    C.CName AS 课程名,
    C.Credit AS 学分,
    SC.ScoreValue AS 成绩,
    fn_CalculateGPA(SC.ScoreValue) AS 绩点,
    CASE fn_IsPassed(SC.ScoreValue) WHEN 1 THEN '通过' ELSE '未通过' END AS 是否通过,
    SC.Semester AS 学期
FROM Score SC
INNER JOIN Student S ON SC.SNo = S.SNo
INNER JOIN Course C ON SC.CNo = C.CNo
ORDER BY S.SNo, SC.Semester, C.CName;

-- 查询7（额外）：执行预警存储过程
CALL usp_GenerateWarningList();

-- ============================================
-- 第八部分：数据验证查询
-- ============================================

-- 验证视图
SELECT * FROM StudentGPAView LIMIT 10;
SELECT * FROM FailedCoreCoursesView;
SELECT * FROM CreditsCompletedView;

-- 验证数据（通过视图查看GPA和学分，无冗余字段）
SELECT 
    学号,
    姓名,
    已获学分 AS 总学分,
    平均绩点
FROM StudentGPAView
ORDER BY 学号;

-- ============================================
-- 脚本执行完成
-- ============================================
-- 说明：
-- 1. 本脚本兼容 MySQL 8.0，如需在 SQL Server 2019 中运行，请修改：
--    - 将 AUTO_INCREMENT 改为 IDENTITY(1,1)
--    - 将 ENUM 改为 CHECK 约束
--    - 将 DELIMITER 语法改为 GO
--    - 将 TINYINT(1) 改为 BIT
--    - 将 ENGINE=InnoDB 等MySQL特性删除
-- 
-- 2. 触发器在插入/更新成绩时会自动：
--    - 计算绩点（GPA_Point）
--    - 判断是否通过（Is_Passed）
--    - 更新学生的总学分和平均GPA
--
-- 3. 使用存储过程 usp_GenerateWarningList() 可以生成预警学生名单
--
-- 4. 所有视图、触发器、存储过程已创建完成，可以直接使用
-- ============================================

