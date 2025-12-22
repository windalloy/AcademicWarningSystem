#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
课程管理界面
"""

import tkinter as tk
from tkinter import ttk, messagebox

class CourseManagementFrame(ttk.Frame):
    """课程管理框架"""
    
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
        
        ttk.Button(toolbar, text="添加", command=self.add_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="修改", command=self.edit_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="刷新", command=self.refresh_data).pack(side=tk.LEFT, padx=2)
        
        # 表格
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("课程号", "课程名", "学分", "课程类型")
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
        
        # 检查数据库连接
        if not self.db_manager.connection or not self.db_manager.cursor:
            return
        
        courses = self.db_manager.get_all_courses()
        if courses:
            for course in courses:
                self.tree.insert("", tk.END, values=(
                    course.get('CNo', ''),
                    course.get('CName', ''),
                    course.get('Credit', 0),
                    course.get('CourseType', '')
                ))
    
    def add_course(self):
        """添加课程"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        dialog = CourseDialog(self, self.db_manager)
        self.wait_window(dialog.dialog)
        self.refresh_data()
    
    def edit_course(self):
        """编辑课程"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要修改的课程")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        dialog = CourseDialog(self, self.db_manager,
                             cno=values[0], cname=values[1],
                             credit=values[2], course_type=values[3])
        self.wait_window(dialog.dialog)
        self.refresh_data()
    
    def delete_course(self):
        """删除课程"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的课程")
            return
        
        item = self.tree.item(selection[0])
        cno = item['values'][0]
        cname = item['values'][1]
        
        if messagebox.askyesno("确认", f"确定要删除课程 {cname} ({cno}) 吗？\n这将同时删除所有相关成绩记录！"):
            if self.db_manager.delete_course(cno):
                messagebox.showinfo("成功", "删除成功")
                self.refresh_data()
            else:
                messagebox.showerror("错误", "删除失败")

class CourseDialog:
    """课程信息对话框"""
    
    def __init__(self, parent, db_manager, cno=None, cname="", credit="", course_type=""):
        self.db_manager = db_manager
        self.cno = cno
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加课程" if not cno else "修改课程")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        self.create_widgets(cno, cname, credit, course_type)
    
    def create_widgets(self, cno, cname, credit, course_type):
        """创建控件"""
        ttk.Label(self.dialog, text="课程号:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.cno_entry = ttk.Entry(self.dialog, width=25)
        self.cno_entry.grid(row=0, column=1, padx=10, pady=10)
        if cno:
            self.cno_entry.insert(0, cno)
            self.cno_entry.config(state='readonly')
        else:
            self.cno_entry.insert(0, "")
        
        ttk.Label(self.dialog, text="课程名:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.cname_entry = ttk.Entry(self.dialog, width=25)
        self.cname_entry.grid(row=1, column=1, padx=10, pady=10)
        self.cname_entry.insert(0, cname)
        
        ttk.Label(self.dialog, text="学分:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.credit_entry = ttk.Entry(self.dialog, width=25)
        self.credit_entry.grid(row=2, column=1, padx=10, pady=10)
        self.credit_entry.insert(0, str(credit) if credit else "")
        
        ttk.Label(self.dialog, text="课程类型:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.type_combo = ttk.Combobox(self.dialog, width=22, values=["核心", "通识", "选修"], state="readonly")
        self.type_combo.grid(row=3, column=1, padx=10, pady=10)
        if course_type:
            self.type_combo.set(course_type)
        
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=30)
        
        ttk.Button(button_frame, text="确定", command=self.save, width=12).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy, width=12).pack(side=tk.LEFT, padx=10)
    
    def save(self):
        """保存"""
        cno = self.cno_entry.get().strip()
        cname = self.cname_entry.get().strip()
        try:
            credit = float(self.credit_entry.get().strip())
        except ValueError:
            messagebox.showerror("错误", "学分必须是数字")
            return
        
        course_type = self.type_combo.get()
        
        if not all([cno, cname, course_type]):
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        if self.cno:
            if self.db_manager.update_course(cno, cname, credit, course_type):
                messagebox.showinfo("成功", "修改成功")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "修改失败")
        else:
            if self.db_manager.add_course(cno, cname, credit, course_type):
                messagebox.showinfo("成功", "添加成功")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "添加失败，课程号可能已存在")

