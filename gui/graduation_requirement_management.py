#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
毕业要求管理界面
"""

import tkinter as tk
from tkinter import ttk, messagebox

class GraduationRequirementManagementFrame(ttk.Frame):
    """毕业要求管理框架"""
    
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
        
        ttk.Button(toolbar, text="添加", command=self.add_requirement).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="修改", command=self.edit_requirement).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_requirement).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="刷新", command=self.refresh_data).pack(side=tk.LEFT, padx=2)
        
        # 表格
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("院系", "总学分要求", "核心课不及格上限", "最低GPA要求")
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
        
        requirements = self.db_manager.get_graduation_requirements()
        if requirements:
            for req in requirements:
                self.tree.insert("", tk.END, values=(
                    req.get('Dept', ''),
                    req.get('TotalCreditRequired', 0),
                    req.get('CoreCourseFailLimit', 0),
                    req.get('MinGPA', 0)
                ))
    
    def add_requirement(self):
        """添加毕业要求"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        dialog = GraduationRequirementDialog(self, self.db_manager)
        self.wait_window(dialog.dialog)
        self.refresh_data()
    
    def edit_requirement(self):
        """编辑毕业要求"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要修改的毕业要求")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        dialog = GraduationRequirementDialog(self, self.db_manager,
                                            dept=values[0],
                                            total_credit=values[1],
                                            fail_limit=values[2],
                                            min_gpa=values[3])
        self.wait_window(dialog.dialog)
        self.refresh_data()
    
    def delete_requirement(self):
        """删除毕业要求"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的毕业要求")
            return
        
        item = self.tree.item(selection[0])
        dept = item['values'][0]
        
        if messagebox.askyesno("确认", f"确定要删除院系 {dept} 的毕业要求吗？"):
            if self.db_manager.delete_graduation_requirement(dept):
                messagebox.showinfo("成功", "删除成功")
                self.refresh_data()
            else:
                messagebox.showerror("错误", "删除失败")

class GraduationRequirementDialog:
    """毕业要求对话框"""
    
    def __init__(self, parent, db_manager, dept=None, total_credit="", fail_limit="", min_gpa=""):
        self.db_manager = db_manager
        self.dept = dept
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加毕业要求" if not dept else "修改毕业要求")
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (350 // 2)
        self.dialog.geometry(f"400x350+{x}+{y}")
        
        self.create_widgets(dept, total_credit, fail_limit, min_gpa)
    
    def create_widgets(self, dept, total_credit, fail_limit, min_gpa):
        """创建控件"""
        ttk.Label(self.dialog, text="院系:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.dept_entry = ttk.Entry(self.dialog, width=25)
        self.dept_entry.grid(row=0, column=1, padx=10, pady=10)
        if dept:
            self.dept_entry.insert(0, dept)
            self.dept_entry.config(state='readonly')
        else:
            self.dept_entry.insert(0, "")
        
        ttk.Label(self.dialog, text="总学分要求:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.total_credit_entry = ttk.Entry(self.dialog, width=25)
        self.total_credit_entry.grid(row=1, column=1, padx=10, pady=10)
        self.total_credit_entry.insert(0, str(total_credit) if total_credit else "")
        
        ttk.Label(self.dialog, text="核心课不及格上限:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.fail_limit_entry = ttk.Entry(self.dialog, width=25)
        self.fail_limit_entry.grid(row=2, column=1, padx=10, pady=10)
        self.fail_limit_entry.insert(0, str(fail_limit) if fail_limit else "")
        
        ttk.Label(self.dialog, text="最低GPA要求:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.min_gpa_entry = ttk.Entry(self.dialog, width=25)
        self.min_gpa_entry.grid(row=3, column=1, padx=10, pady=10)
        self.min_gpa_entry.insert(0, str(min_gpa) if min_gpa else "")
        
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=30)
        
        ttk.Button(button_frame, text="确定", command=self.save, width=12).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy, width=12).pack(side=tk.LEFT, padx=10)
    
    def save(self):
        """保存"""
        dept = self.dept_entry.get().strip()
        try:
            total_credit = float(self.total_credit_entry.get().strip())
            fail_limit = int(self.fail_limit_entry.get().strip())
            min_gpa = float(self.min_gpa_entry.get().strip())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        if not dept:
            messagebox.showerror("错误", "请填写院系")
            return
        
        if self.dept:
            if self.db_manager.update_graduation_requirement(dept, total_credit, fail_limit, min_gpa):
                messagebox.showinfo("成功", "修改成功")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "修改失败")
        else:
            if self.db_manager.add_graduation_requirement(dept, total_credit, fail_limit, min_gpa):
                messagebox.showinfo("成功", "添加成功")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "添加失败，该院系的毕业要求可能已存在")

