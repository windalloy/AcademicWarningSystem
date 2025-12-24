#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查询分析界面
"""

import tkinter as tk
from tkinter import ttk, messagebox

class QueryFrame(ttk.Frame):
    """查询分析框架"""
    
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.create_widgets()
    
    def create_widgets(self):
        """创建控件"""
        # 左侧：查询选项
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(left_frame, text="查询选项", font=("Arial", 12, "bold")).pack(pady=10)
        
        query_options = [
            ("预警学生名单", self.query_warning_list),
            ("学生GPA排名", self.query_gpa_ranking),
            ("核心课程不及格", self.query_failed_core_courses),
            ("所有未通过课程", self.query_failed_courses),
            ("学分完成情况", self.query_credits),
            ("院系统计", self.query_department_stats),
            ("学期统计", self.query_semester_stats),
        ]
        
        for text, command in query_options:
            ttk.Button(left_frame, text=text, command=command, width=20).pack(pady=5, padx=5)
        
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Button(left_frame, text="刷新", command=self.refresh_data, width=20).pack(pady=5)
        
        # 右侧：结果显示
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(right_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 文本框显示结果
        self.result_text = tk.Text(right_frame, yscrollcommand=scrollbar.set, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar.config(command=self.result_text.yview)
        self.result_text.pack(fill=tk.BOTH, expand=True)
    
    def refresh_data(self):
        """刷新数据"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "请选择左侧的查询选项...")
    
    def display_result(self, title, data, columns=None):
        """显示查询结果"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"{title}\n")
        self.result_text.insert(tk.END, "=" * 80 + "\n\n")
        
        if not data:
            self.result_text.insert(tk.END, "没有找到数据\n")
            return
        
        # 如果有列名，显示表头
        if columns:
            header = " | ".join(columns)
            self.result_text.insert(tk.END, header + "\n")
            self.result_text.insert(tk.END, "-" * len(header) + "\n")
        
        # 显示数据
        for row in data:
            if isinstance(row, dict):
                # 字典格式
                values = [str(row.get(k, '')) for k in row.keys()]
                self.result_text.insert(tk.END, " | ".join(values) + "\n")
            else:
                # 列表/元组格式
                self.result_text.insert(tk.END, " | ".join(str(v) for v in row) + "\n")
        
        self.result_text.insert(tk.END, f"\n共 {len(data)} 条记录\n")
    
    def query_warning_list(self):
        """查询预警学生名单"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        try:
            results = self.db_manager.get_warning_list()
            if results:
                self.display_result("预警学生名单", results, 
                                  ["学号", "姓名", "院系", "预警原因", "已获学分", "要求学分", "核心课程不及格数", "不及格上限"])
            else:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "预警学生名单\n" + "=" * 80 + "\n\n没有预警学生\n")
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
    
    def query_gpa_ranking(self):
        """查询GPA排名"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        try:
            results = self.db_manager.get_student_gpa_view()
            if results:
                self.display_result("学生GPA排名", results, ["学号", "姓名", "院系", "已获学分", "平均绩点"])
            else:
                self.display_result("学生GPA排名", [])
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
    
    def query_failed_core_courses(self):
        """查询核心课程不及格"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        try:
            results = self.db_manager.get_failed_core_courses()
            if results:
                self.display_result("核心课程不及格记录", results, ["学号", "姓名", "课程名", "成绩", "学期"])
            else:
                self.display_result("核心课程不及格记录", [])
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
    
    def query_failed_courses(self):
        """查询所有未通过课程"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        try:
            results = self.db_manager.get_failed_courses()
            if results:
                self.display_result("所有未通过课程", results, ["学号", "姓名", "院系", "课程号", "课程名", "学分", "课程类型", "成绩", "学期"])
            else:
                self.display_result("所有未通过课程", [])
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
    
    def query_credits(self):
        """查询学分完成情况"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        try:
            results = self.db_manager.get_credits_completed()
            if results:
                self.display_result("学分完成情况", results, ["学号", "姓名", "已获学分总数"])
            else:
                self.display_result("学分完成情况", [])
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
    
    def query_department_stats(self):
        """查询院系统计"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        try:
            results = self.db_manager.get_department_statistics()
            if results:
                self.display_result("各院系统计", results, ["院系", "学生人数", "平均GPA", "平均已获学分"])
            else:
                self.display_result("各院系统计", [])
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
    
    def query_semester_stats(self):
        """查询学期统计"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        try:
            results = self.db_manager.get_semester_statistics()
            if results:
                self.display_result("学期统计", results, ["学期", "选课学生数", "总选课数", "开设课程数", "平均成绩"])
            else:
                self.display_result("学期统计", [])
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")

