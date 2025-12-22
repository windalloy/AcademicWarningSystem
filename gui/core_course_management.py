#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
核心课程管理界面
"""

import tkinter as tk
from tkinter import ttk, messagebox

class CoreCourseManagementFrame(ttk.Frame):
    """核心课程管理框架"""
    
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
        
        ttk.Button(toolbar, text="添加", command=self.add_core_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_core_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="刷新", command=self.refresh_data).pack(side=tk.LEFT, padx=2)
        
        # 表格
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("院系", "课程号", "课程名")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def refresh_data(self):
        """刷新数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.db_manager.connection or not self.db_manager.cursor:
            return
        
        core_courses = self.db_manager.get_core_courses()
        if core_courses:
            # 获取课程信息
            courses = self.db_manager.get_all_courses()
            course_dict = {c.get('CNo'): c.get('CName') for c in courses}
            
            for cc in core_courses:
                cno = cc.get('CNo', '')
                self.tree.insert("", tk.END, values=(
                    cc.get('Dept', ''),
                    cno,
                    course_dict.get(cno, '未知课程')
                ))
    
    def add_core_course(self):
        """添加核心课程"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        dialog = CoreCourseDialog(self, self.db_manager)
        self.wait_window(dialog.dialog)
        self.refresh_data()
    
    def delete_core_course(self):
        """删除核心课程"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的核心课程")
            return
        
        item = self.tree.item(selection[0])
        dept = item['values'][0]
        cno = item['values'][1]
        
        if messagebox.askyesno("确认", f"确定要删除 {dept} 的核心课程 {cno} 吗？"):
            if self.db_manager.delete_core_course(dept, cno):
                messagebox.showinfo("成功", "删除成功")
                self.refresh_data()
            else:
                messagebox.showerror("错误", "删除失败")

class CoreCourseDialog:
    """核心课程对话框"""
    
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加核心课程")
        self.dialog.geometry("400x220")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (220 // 2)
        self.dialog.geometry(f"400x220+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建控件"""
        # 获取所有院系
        students = self.db_manager.get_all_students()
        depts = list(set([s.get('Dept', '') for s in students if s.get('Dept')]))
        
        ttk.Label(self.dialog, text="院系:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.dept_combo = ttk.Combobox(self.dialog, width=22, values=depts)
        self.dept_combo.grid(row=0, column=1, padx=10, pady=10)
        
        # 获取所有课程
        courses = self.db_manager.get_all_courses()
        course_list = [f"{c.get('CNo')} - {c.get('CName')}" for c in courses]
        
        ttk.Label(self.dialog, text="课程:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.course_combo = ttk.Combobox(self.dialog, width=22, values=course_list, state="readonly")
        self.course_combo.grid(row=1, column=1, padx=10, pady=10)
        
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=30)
        
        ttk.Button(button_frame, text="确定", command=self.save, width=12).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy, width=12).pack(side=tk.LEFT, padx=10)
    
    def save(self):
        """保存"""
        dept = self.dept_combo.get().strip()
        course_text = self.course_combo.get().strip()
        
        if not dept or not course_text:
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        cno = course_text.split(' - ')[0]
        
        if self.db_manager.add_core_course(dept, cno):
            messagebox.showinfo("成功", "添加成功")
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", "添加失败，该核心课程可能已存在")

