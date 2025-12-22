#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
学生管理界面
"""

import tkinter as tk
from tkinter import ttk, messagebox

class StudentManagementFrame(ttk.Frame):
    """学生管理框架"""
    
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.create_widgets()
        # 延迟刷新，等待数据库连接
        self.after(100, self.refresh_data)
    
    def create_widgets(self):
        """创建控件"""
        # 工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="添加", command=self.add_student).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="修改", command=self.edit_student).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_student).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="刷新", command=self.refresh_data).pack(side=tk.LEFT, padx=2)
        
        # 表格
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 树形视图
        columns = ("学号", "姓名", "院系", "入学年份", "总学分", "GPA")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # 设置列
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def refresh_data(self):
        """刷新数据"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 检查数据库连接
        if not self.db_manager.connection or not self.db_manager.cursor:
            return
        
        # 获取数据（通过视图获取，包含计算后的学分和GPA）
        students = self.db_manager.get_all_students_with_gpa()
        if students:
            for student in students:
                self.tree.insert("", tk.END, values=(
                    student.get('学号', ''),
                    student.get('姓名', ''),
                    student.get('院系', ''),
                    student.get('EnrollmentYear', 0),
                    student.get('已获学分', 0),
                    student.get('平均绩点', 0)
                ))
    
    def add_student(self):
        """添加学生"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        dialog = StudentDialog(self, self.db_manager)
        self.wait_window(dialog.dialog)
        self.refresh_data()
    
    def edit_student(self):
        """编辑学生"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要修改的学生")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        dialog = StudentDialog(self, self.db_manager, 
                              sno=values[0], sname=values[1], 
                              dept=values[2], year=values[3])
        self.wait_window(dialog.dialog)
        self.refresh_data()
    
    def delete_student(self):
        """删除学生"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的学生")
            return
        
        item = self.tree.item(selection[0])
        sno = item['values'][0]
        sname = item['values'][1]
        
        if messagebox.askyesno("确认", f"确定要删除学生 {sname} ({sno}) 吗？\n这将同时删除该学生的所有成绩记录！"):
            if self.db_manager.delete_student(sno):
                messagebox.showinfo("成功", "删除成功")
                self.refresh_data()
            else:
                messagebox.showerror("错误", "删除失败")

class StudentDialog:
    """学生信息对话框"""
    
    def __init__(self, parent, db_manager, sno=None, sname="", dept="", year=""):
        self.db_manager = db_manager
        self.sno = sno
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加学生" if not sno else "修改学生")
        self.dialog.geometry("400x280")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (280 // 2)
        self.dialog.geometry(f"400x280+{x}+{y}")
        
        self.create_widgets(sno, sname, dept, year)
    
    def create_widgets(self, sno, sname, dept, year):
        """创建控件"""
        # 学号
        ttk.Label(self.dialog, text="学号:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.sno_entry = ttk.Entry(self.dialog, width=25)
        self.sno_entry.grid(row=0, column=1, padx=10, pady=10)
        if sno:
            self.sno_entry.insert(0, sno)
            self.sno_entry.config(state='readonly')
        else:
            self.sno_entry.insert(0, "")
        
        # 姓名
        ttk.Label(self.dialog, text="姓名:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.sname_entry = ttk.Entry(self.dialog, width=25)
        self.sname_entry.grid(row=1, column=1, padx=10, pady=10)
        self.sname_entry.insert(0, sname)
        
        # 院系
        ttk.Label(self.dialog, text="院系:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.dept_entry = ttk.Entry(self.dialog, width=25)
        self.dept_entry.grid(row=2, column=1, padx=10, pady=10)
        self.dept_entry.insert(0, dept)
        
        # 入学年份
        ttk.Label(self.dialog, text="入学年份:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.year_entry = ttk.Entry(self.dialog, width=25)
        self.year_entry.grid(row=3, column=1, padx=10, pady=10)
        self.year_entry.insert(0, str(year) if year else "")
        
        # 按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=30)
        
        ttk.Button(button_frame, text="确定", command=self.save, width=12).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy, width=12).pack(side=tk.LEFT, padx=10)
    
    def save(self):
        """保存"""
        sno = self.sno_entry.get().strip()
        sname = self.sname_entry.get().strip()
        dept = self.dept_entry.get().strip()
        try:
            year = int(self.year_entry.get().strip())
        except ValueError:
            messagebox.showerror("错误", "入学年份必须是数字")
            return
        
        if not all([sno, sname, dept]):
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        if self.sno:
            # 更新
            if self.db_manager.update_student(sno, sname, dept, year):
                messagebox.showinfo("成功", "修改成功")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "修改失败")
        else:
            # 添加
            if self.db_manager.add_student(sno, sname, dept, year):
                messagebox.showinfo("成功", "添加成功")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "添加失败，学号可能已存在")

