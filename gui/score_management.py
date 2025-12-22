#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
成绩管理界面
"""

import tkinter as tk
from tkinter import ttk, messagebox

class ScoreManagementFrame(ttk.Frame):
    """成绩管理框架"""
    
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
        
        ttk.Button(toolbar, text="添加", command=self.add_score).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="修改", command=self.edit_score).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_score).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="刷新", command=self.refresh_data).pack(side=tk.LEFT, padx=2)
        
        # 表格
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("学号", "姓名", "课程名", "成绩", "绩点", "是否通过", "学期")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def refresh_data(self):
        """刷新数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 检查数据库连接
        if not self.db_manager.connection or not self.db_manager.cursor:
            return
        
        scores = self.db_manager.get_all_scores()
        if scores:
            for score in scores:
                try:
                    score_value = float(score.get('ScoreValue', 0)) if score.get('ScoreValue') is not None else 0
                    # 通过函数计算绩点和是否通过
                    gpa_point = self.db_manager.calculate_gpa(score_value)
                    is_passed = "通过" if score_value >= 60 else "未通过"
                    self.tree.insert("", tk.END, values=(
                        score.get('SNo', ''),
                        score.get('SName', ''),
                        score.get('CName', ''),
                        score_value,
                        gpa_point,
                        is_passed,
                        score.get('Semester', '')
                    ))
                except Exception as e:
                    print(f"处理成绩记录时出错: {e}, 记录: {score}")
                    continue
    
    def add_score(self):
        """添加成绩"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        dialog = ScoreDialog(self, self.db_manager)
        self.wait_window(dialog.dialog)
        self.refresh_data()
    
    def edit_score(self):
        """编辑成绩"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要修改的成绩")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        dialog = ScoreDialog(self, self.db_manager,
                           sno=values[0], cname=values[2],
                           score=values[3], semester=values[6])
        self.wait_window(dialog.dialog)
        self.refresh_data()
    
    def delete_score(self):
        """删除成绩"""
        if not self.db_manager.connection or not self.db_manager.cursor:
            messagebox.showwarning("警告", "请先连接数据库")
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的成绩")
            return
        
        item = self.tree.item(selection[0])
        sno = item['values'][0]
        cname = item['values'][2]
        semester = item['values'][6]
        
        # 获取课程号
        courses = self.db_manager.get_all_courses()
        cno = None
        for course in courses:
            if course.get('CName') == cname:
                cno = course.get('CNo')
                break
        
        if cno and messagebox.askyesno("确认", f"确定要删除这条成绩记录吗？"):
            if self.db_manager.delete_score(sno, cno, semester):
                messagebox.showinfo("成功", "删除成功")
                self.refresh_data()
            else:
                messagebox.showerror("错误", "删除失败")

class ScoreDialog:
    """成绩信息对话框"""
    
    def __init__(self, parent, db_manager, sno=None, cname="", score="", semester=""):
        self.db_manager = db_manager
        self.sno = sno
        self.cname = cname
        self.semester = semester
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加成绩" if not sno else "修改成绩")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        self.create_widgets(sno, cname, score, semester)
    
    def create_widgets(self, sno, cname, score, semester):
        """创建控件"""
        # 学号
        ttk.Label(self.dialog, text="学号:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.sno_combo = ttk.Combobox(self.dialog, width=22, state="readonly")
        self.sno_combo.grid(row=0, column=1, padx=10, pady=10)
        students = self.db_manager.get_all_students()
        if students:
            self.sno_combo['values'] = [f"{s.get('SNo')} - {s.get('SName')}" for s in students]
            if sno:
                for s in students:
                    if s.get('SNo') == sno:
                        self.sno_combo.set(f"{sno} - {s.get('SName')}")
                        self.sno_combo.config(state='readonly')
                        break
        
        # 课程
        ttk.Label(self.dialog, text="课程:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.course_combo = ttk.Combobox(self.dialog, width=22, state="readonly")
        self.course_combo.grid(row=1, column=1, padx=10, pady=10)
        courses = self.db_manager.get_all_courses()
        if courses:
            self.course_combo['values'] = [f"{c.get('CNo')} - {c.get('CName')}" for c in courses]
            if cname:
                for c in courses:
                    if c.get('CName') == cname:
                        self.course_combo.set(f"{c.get('CNo')} - {cname}")
                        self.course_combo.config(state='readonly')
                        break
        
        # 成绩
        ttk.Label(self.dialog, text="成绩:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.score_entry = ttk.Entry(self.dialog, width=25)
        self.score_entry.grid(row=2, column=1, padx=10, pady=10)
        self.score_entry.insert(0, str(score) if score else "")
        
        # 学期
        ttk.Label(self.dialog, text="学期:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.semester_entry = ttk.Entry(self.dialog, width=25)
        self.semester_entry.grid(row=3, column=1, padx=10, pady=10)
        self.semester_entry.insert(0, semester)
        if self.sno:
            self.semester_entry.config(state='readonly')
        
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=30)
        
        ttk.Button(button_frame, text="确定", command=self.save, width=12).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy, width=12).pack(side=tk.LEFT, padx=10)
    
    def save(self):
        """保存"""
        sno_text = self.sno_combo.get()
        if not sno_text:
            messagebox.showerror("错误", "请选择学生")
            return
        sno = sno_text.split(' - ')[0]
        
        course_text = self.course_combo.get()
        if not course_text:
            messagebox.showerror("错误", "请选择课程")
            return
        cno = course_text.split(' - ')[0]
        
        try:
            score_value = float(self.score_entry.get().strip())
            if score_value < 0 or score_value > 100:
                messagebox.showerror("错误", "成绩必须在0-100之间")
                return
        except ValueError:
            messagebox.showerror("错误", "成绩必须是数字")
            return
        
        semester = self.semester_entry.get().strip()
        if not semester:
            messagebox.showerror("错误", "请填写学期")
            return
        
        if self.sno:
            # 更新
            if self.db_manager.update_score(sno, cno, semester, score_value):
                messagebox.showinfo("成功", "修改成功")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "修改失败")
        else:
            # 添加
            if self.db_manager.add_score(sno, cno, score_value, semester):
                messagebox.showinfo("成功", "添加成功")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "添加失败，该学生该课程该学期的成绩可能已存在")

