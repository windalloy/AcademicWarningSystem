#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主窗口界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from gui.connection_dialog import ConnectionDialog
from gui.student_management import StudentManagementFrame
from gui.course_management import CourseManagementFrame
from gui.score_management import ScoreManagementFrame
from gui.graduation_requirement_management import GraduationRequirementManagementFrame
from gui.core_course_management import CoreCourseManagementFrame
from gui.query_frame import QueryFrame

class MainWindow:
    """主窗口类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("大学生学业预警与成绩分析系统")
        self.root.geometry("1200x700")
        
        self.db_manager = DatabaseManager()
        self.connected = False
        
        self.create_menu()
        self.create_toolbar()
        self.create_notebook()
        
        # 检查数据库连接
        self.check_connection()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="数据库连接", command=self.show_connection_dialog)
        file_menu.add_command(label="初始化数据库", command=self.initialize_database)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="连接数据库", command=self.show_connection_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="初始化数据库", command=self.initialize_database).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.status_label = ttk.Label(toolbar, text="未连接", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=10)
    
    def create_notebook(self):
        """创建标签页"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 学生管理
        self.student_frame = StudentManagementFrame(self.notebook, self.db_manager)
        self.notebook.add(self.student_frame, text="学生管理")
        
        # 课程管理
        self.course_frame = CourseManagementFrame(self.notebook, self.db_manager)
        self.notebook.add(self.course_frame, text="课程管理")
        
        # 成绩管理
        self.score_frame = ScoreManagementFrame(self.notebook, self.db_manager)
        self.notebook.add(self.score_frame, text="成绩管理")
        
        # 毕业要求管理
        self.graduation_frame = GraduationRequirementManagementFrame(self.notebook, self.db_manager)
        self.notebook.add(self.graduation_frame, text="毕业要求")
        
        # 核心课程管理
        self.core_course_frame = CoreCourseManagementFrame(self.notebook, self.db_manager)
        self.notebook.add(self.core_course_frame, text="核心课程")
        
        # 查询分析
        self.query_frame = QueryFrame(self.notebook, self.db_manager)
        self.notebook.add(self.query_frame, text="查询分析")
    
    def check_connection(self):
        """检查数据库连接"""
        if self.db_manager.connect():
            self.connected = True
            self.status_label.config(text="已连接", foreground="green")
            # 连接成功后自动刷新所有标签页
            self.refresh_all_tabs()
        else:
            self.connected = False
            self.status_label.config(text="未连接", foreground="red")
    
    def show_connection_dialog(self):
        """显示连接对话框"""
        dialog = ConnectionDialog(self.root, self.db_manager)
        self.root.wait_window(dialog.dialog)
        self.check_connection()
    
    def initialize_database(self):
        """初始化数据库"""
        if not messagebox.askyesno("确认", "这将重新创建数据库和所有表，现有数据将被删除！\n是否继续？"):
            return
        
        sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "AcademicWarningSystem.sql")
        if not os.path.exists(sql_file):
            messagebox.showerror("错误", f"找不到SQL文件: {sql_file}")
            return
        
        if self.db_manager.initialize_database(sql_file):
            messagebox.showinfo("成功", "数据库初始化成功！")
            self.check_connection()
            # 初始化后自动刷新所有标签页
            self.refresh_all_tabs()
        else:
            messagebox.showerror("错误", "数据库初始化失败，请检查控制台输出")
    
    def refresh_all_tabs(self):
        """刷新所有标签页"""
        # 确保数据库已连接
        if not self.db_manager.connection or not self.db_manager.cursor:
            return
        
        if hasattr(self, 'student_frame'):
            try:
                self.student_frame.refresh_data()
            except Exception as e:
                print(f"刷新学生管理失败: {e}")
        if hasattr(self, 'course_frame'):
            try:
                self.course_frame.refresh_data()
            except Exception as e:
                print(f"刷新课程管理失败: {e}")
        if hasattr(self, 'score_frame'):
            try:
                self.score_frame.refresh_data()
            except Exception as e:
                print(f"刷新成绩管理失败: {e}")
        if hasattr(self, 'graduation_frame'):
            try:
                self.graduation_frame.refresh_data()
            except Exception as e:
                print(f"刷新毕业要求失败: {e}")
        if hasattr(self, 'core_course_frame'):
            try:
                self.core_course_frame.refresh_data()
            except Exception as e:
                print(f"刷新核心课程失败: {e}")
        if hasattr(self, 'query_frame'):
            try:
                self.query_frame.refresh_data()
            except Exception as e:
                print(f"刷新查询分析失败: {e}")
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """
大学生学业预警与成绩分析系统

版本：1.0
开发语言：Python + MySQL
界面框架：Tkinter

功能特点：
- 学生信息管理
- 课程信息管理
- 成绩录入与查询
- 自动计算GPA和学分
- 学业预警分析
- 数据统计分析

© 2024
        """
        messagebox.showinfo("关于", about_text)

