#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库管理模块
负责数据库连接、初始化、CRUD操作等
"""

import mysql.connector
from mysql.connector import Error
import os
import sys

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'database': 'AcademicWarningSystem',
            'charset': 'utf8mb4'
        }
    
    def set_config(self, host, port, user, password, database):
        """设置数据库连接配置"""
        self.config['host'] = host
        self.config['port'] = port
        self.config['user'] = user
        self.config['password'] = password
        self.config['database'] = database
    
    def connect(self):
        """连接到数据库"""
        try:
            # 先尝试连接（不指定数据库）
            temp_config = self.config.copy()
            database_name = temp_config.pop('database', None)
            
            # 连接到MySQL服务器
            self.connection = mysql.connector.connect(**temp_config)
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                
                # 如果指定了数据库，检查是否存在，不存在则创建
                if database_name:
                    self.cursor.execute("SHOW DATABASES LIKE %s", (database_name,))
                    if not self.cursor.fetchone():
                        # 数据库不存在，创建它
                        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                        self.connection.commit()
                    
                    # 切换到指定数据库
                    self.cursor.execute(f"USE `{database_name}`")
                
                return True
        except Error as e:
            print(f"数据库连接错误: {e}")
            return False
        return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_sql_file(self, file_path):
        """执行SQL文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # 使用MySQL的multi_statement模式执行
            # 先分割出完整的SQL语句
            statements = []
            current_statement = ""
            in_delimiter_block = False
            delimiter = ";"
            
            for line in sql_script.split('\n'):
                original_line = line
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('--'):
                    continue
                
                # 处理DELIMITER
                if line.upper().startswith('DELIMITER'):
                    if '$$' in line:
                        delimiter = "$$"
                        in_delimiter_block = True
                    else:
                        delimiter = ";"
                        in_delimiter_block = False
                    continue
                
                # 累积语句
                current_statement += original_line + "\n"
                
                # 检查是否到达语句结束
                if line.endswith(delimiter):
                    stmt = current_statement.rstrip().rstrip(delimiter).strip()
                    if stmt:
                        statements.append(stmt)
                    current_statement = ""
            
            # 如果有剩余的语句
            if current_statement.strip():
                statements.append(current_statement.strip())
            
            # 执行每个SQL语句
            for statement in statements:
                if statement:
                    try:
                        # 对于包含多行值的INSERT语句，需要完整执行
                        # 使用executemany对于批量INSERT更高效，但这里使用execute更简单
                        self.cursor.execute(statement)
                        self.connection.commit()
                    except Error as e:
                        # 某些语句可能失败（如DROP TABLE IF EXISTS），继续执行
                        error_msg = str(e).lower()
                        if "doesn't exist" not in error_msg:
                            # 对于重复键错误，也继续执行（可能是重复初始化）
                            if "duplicate entry" not in error_msg:
                                print(f"执行SQL时出错: {e}")
                                # 只打印前200个字符
                                sql_preview = statement[:200] if len(statement) > 200 else statement
                                print(f"SQL预览: {sql_preview}...")
            
            return True
        except Exception as e:
            print(f"执行SQL文件错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def initialize_database(self, sql_file_path):
        """初始化数据库（执行SQL脚本）"""
        # 先连接到MySQL服务器（不指定数据库）
        temp_config = self.config.copy()
        temp_config.pop('database', None)
        
        try:
            temp_conn = mysql.connector.connect(**temp_config)
            temp_cursor = temp_conn.cursor()
            
            # 创建数据库（如果不存在）
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            temp_conn.commit()
            
            temp_cursor.close()
            temp_conn.close()
            
            # 连接到目标数据库
            if self.connect():
                return self.execute_sql_file(sql_file_path)
        except Error as e:
            print(f"初始化数据库错误: {e}")
            return False
        return False
    
    def execute_query(self, query, params=None):
        """执行查询（SELECT）"""
        if not self.connection or not self.cursor:
            return []
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询错误: {e}")
            return []
    
    def execute_update(self, query, params=None):
        """执行更新（INSERT, UPDATE, DELETE）"""
        if not self.connection or not self.cursor:
            return False
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Error as e:
            if self.connection:
                self.connection.rollback()
            print(f"更新错误: {e}")
            return False
    
    def call_procedure(self, procedure_name, params=None):
        """调用存储过程"""
        if not self.connection or not self.cursor:
            return []
        try:
            if params:
                self.cursor.callproc(procedure_name, params)
            else:
                self.cursor.callproc(procedure_name)
            
            results = []
            for result in self.cursor.stored_results():
                results.extend(result.fetchall())
            return results
        except Error as e:
            print(f"调用存储过程错误: {e}")
            return []
    
    # ========== 学生管理 ==========
    def get_all_students(self):
        """获取所有学生（基础信息）"""
        query = "SELECT * FROM Student ORDER BY SNo"
        return self.execute_query(query)
    
    def get_all_students_with_gpa(self):
        """获取所有学生（包含GPA和学分，通过视图计算）"""
        query = """
            SELECT 
                S.SNo AS 学号,
                S.SName AS 姓名,
                S.Dept AS 院系,
                S.EnrollmentYear,
                SG.已获学分,
                SG.平均绩点
            FROM Student S
            LEFT JOIN StudentGPAView SG ON S.SNo = SG.学号
            ORDER BY S.SNo
        """
        return self.execute_query(query)
    
    def add_student(self, sno, sname, dept, year):
        """添加学生"""
        query = "INSERT INTO Student (SNo, SName, Dept, EnrollmentYear) VALUES (%s, %s, %s, %s)"
        return self.execute_update(query, (sno, sname, dept, year))
    
    def update_student(self, sno, sname, dept, year):
        """更新学生信息"""
        query = "UPDATE Student SET SName=%s, Dept=%s, EnrollmentYear=%s WHERE SNo=%s"
        return self.execute_update(query, (sname, dept, year, sno))
    
    def delete_student(self, sno):
        """删除学生（级联删除成绩）"""
        query = "DELETE FROM Student WHERE SNo=%s"
        return self.execute_update(query, (sno,))
    
    # ========== 课程管理 ==========
    def get_all_courses(self):
        """获取所有课程"""
        query = "SELECT * FROM Course ORDER BY CNo"
        return self.execute_query(query)
    
    def add_course(self, cno, cname, credit, course_type):
        """添加课程"""
        query = "INSERT INTO Course (CNo, CName, Credit, CourseType) VALUES (%s, %s, %s, %s)"
        return self.execute_update(query, (cno, cname, credit, course_type))
    
    def update_course(self, cno, cname, credit, course_type):
        """更新课程"""
        query = "UPDATE Course SET CName=%s, Credit=%s, CourseType=%s WHERE CNo=%s"
        return self.execute_update(query, (cname, credit, course_type, cno))
    
    def delete_course(self, cno):
        """删除课程"""
        query = "DELETE FROM Course WHERE CNo=%s"
        return self.execute_update(query, (cno,))
    
    # ========== 成绩管理 ==========
    def calculate_gpa(self, score_value):
        """计算绩点（Python端计算，与数据库函数fn_CalculateGPA一致）"""
        if score_value >= 90:
            return 4.0
        elif score_value >= 80:
            return 3.0
        elif score_value >= 70:
            return 2.0
        elif score_value >= 60:
            return 1.0
        else:
            return 0.0
    
    def get_all_scores(self):
        """获取所有成绩（不包含冗余字段）"""
        query = """
            SELECT SC.SNo, SC.CNo, SC.ScoreValue, SC.Semester, S.SName, C.CName, C.Credit
            FROM Score SC
            INNER JOIN Student S ON SC.SNo = S.SNo
            INNER JOIN Course C ON SC.CNo = C.CNo
            ORDER BY SC.SNo, SC.Semester
        """
        return self.execute_query(query)
    
    def get_student_scores(self, sno):
        """获取指定学生的成绩（不包含冗余字段）"""
        query = """
            SELECT SC.SNo, SC.CNo, SC.ScoreValue, SC.Semester, C.CName, C.Credit, C.CourseType
            FROM Score SC
            INNER JOIN Course C ON SC.CNo = C.CNo
            WHERE SC.SNo = %s
            ORDER BY SC.Semester, C.CName
        """
        return self.execute_query(query, (sno,))
    
    def add_score(self, sno, cno, score_value, semester):
        """添加成绩（触发器会自动计算GPA和是否通过）"""
        query = "INSERT INTO Score (SNo, CNo, ScoreValue, Semester) VALUES (%s, %s, %s, %s)"
        return self.execute_update(query, (sno, cno, score_value, semester))
    
    def update_score(self, sno, cno, semester, score_value):
        """更新成绩"""
        query = "UPDATE Score SET ScoreValue=%s WHERE SNo=%s AND CNo=%s AND Semester=%s"
        return self.execute_update(query, (score_value, sno, cno, semester))
    
    def delete_score(self, sno, cno, semester):
        """删除成绩"""
        query = "DELETE FROM Score WHERE SNo=%s AND CNo=%s AND Semester=%s"
        return self.execute_update(query, (sno, cno, semester))
    
    # ========== 查询功能 ==========
    def get_warning_list(self):
        """获取预警学生名单"""
        return self.call_procedure('usp_GenerateWarningList')
    
    def get_failed_core_courses(self, sno=None):
        """获取核心课程不及格"""
        if sno:
            query = """
                SELECT * FROM FailedCoreCoursesView WHERE 学号 = %s
            """
            return self.execute_query(query, (sno,))
        else:
            query = "SELECT * FROM FailedCoreCoursesView"
            return self.execute_query(query)
    
    def get_student_gpa_view(self):
        """获取学生GPA视图"""
        query = "SELECT * FROM StudentGPAView ORDER BY 平均绩点 DESC"
        return self.execute_query(query)
    
    def get_credits_completed(self):
        """获取学分完成情况"""
        query = "SELECT * FROM CreditsCompletedView ORDER BY 已获学分总数 DESC"
        return self.execute_query(query)
    
    def get_department_statistics(self):
        """获取各院系统计"""
        query = """
            SELECT 
                S.Dept AS 院系,
                COUNT(*) AS 学生人数,
                ROUND(AVG(S.GPA), 2) AS 平均GPA,
                ROUND(AVG(S.TotalCredit), 2) AS 平均已获学分
            FROM Student S
            GROUP BY S.Dept
            ORDER BY 平均GPA DESC
        """
        return self.execute_query(query)
    
    def get_semester_statistics(self):
        """获取学期统计"""
        query = """
            SELECT 
                SC.Semester AS 学期,
                COUNT(DISTINCT SC.SNo) AS 选课学生数,
                COUNT(*) AS 总选课数,
                COUNT(DISTINCT SC.CNo) AS 开设课程数,
                ROUND(AVG(SC.ScoreValue), 2) AS 平均成绩
            FROM Score SC
            GROUP BY SC.Semester
            ORDER BY SC.Semester
        """
        return self.execute_query(query)
    
    # ========== 毕业要求管理 ==========
    def get_graduation_requirements(self):
        """获取毕业要求"""
        query = "SELECT * FROM GraduationRequirement ORDER BY Dept"
        return self.execute_query(query)
    
    def add_graduation_requirement(self, dept, total_credit, fail_limit, min_gpa):
        """添加毕业要求"""
        query = "INSERT INTO GraduationRequirement (Dept, TotalCreditRequired, CoreCourseFailLimit, MinGPA) VALUES (%s, %s, %s, %s)"
        return self.execute_update(query, (dept, total_credit, fail_limit, min_gpa))
    
    def update_graduation_requirement(self, dept, total_credit, fail_limit, min_gpa):
        """更新毕业要求"""
        query = "UPDATE GraduationRequirement SET TotalCreditRequired=%s, CoreCourseFailLimit=%s, MinGPA=%s WHERE Dept=%s"
        return self.execute_update(query, (total_credit, fail_limit, min_gpa, dept))
    
    def delete_graduation_requirement(self, dept):
        """删除毕业要求"""
        query = "DELETE FROM GraduationRequirement WHERE Dept=%s"
        return self.execute_update(query, (dept,))
    
    # ========== 核心课程管理 ==========
    def get_core_courses(self, dept=None):
        """获取核心课程"""
        if dept:
            query = "SELECT * FROM CoreCourse WHERE Dept = %s"
            return self.execute_query(query, (dept,))
        else:
            query = "SELECT * FROM CoreCourse ORDER BY Dept, CNo"
            return self.execute_query(query)
    
    def add_core_course(self, dept, cno):
        """添加核心课程"""
        query = "INSERT INTO CoreCourse (Dept, CNo) VALUES (%s, %s)"
        return self.execute_update(query, (dept, cno))
    
    def delete_core_course(self, dept, cno):
        """删除核心课程"""
        query = "DELETE FROM CoreCourse WHERE Dept=%s AND CNo=%s"
        return self.execute_update(query, (dept, cno))
    
    # ========== 未通过课程查询 ==========
    def get_failed_courses(self, sno=None):
        """获取未通过课程（所有课程，不仅仅是核心课程）"""
        if sno:
            query = "SELECT * FROM FailedCoursesView WHERE 学号 = %s"
            return self.execute_query(query, (sno,))
        else:
            query = "SELECT * FROM FailedCoursesView"
            return self.execute_query(query)

