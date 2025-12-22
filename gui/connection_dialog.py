#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库连接对话框
"""

import tkinter as tk
from tkinter import ttk, messagebox

class ConnectionDialog:
    """数据库连接对话框"""
    
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("数据库连接设置")
        self.dialog.geometry("450x320")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (320 // 2)
        self.dialog.geometry(f"450x320+{x}+{y}")
        
        self.create_widgets()
        self.load_current_config()
    
    def create_widgets(self):
        """创建控件"""
        # 主机
        ttk.Label(self.dialog, text="主机:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.host_entry = ttk.Entry(self.dialog, width=30)
        self.host_entry.grid(row=0, column=1, padx=10, pady=10)
        self.host_entry.insert(0, "localhost")
        
        # 端口
        ttk.Label(self.dialog, text="端口:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.port_entry = ttk.Entry(self.dialog, width=30)
        self.port_entry.grid(row=1, column=1, padx=10, pady=10)
        self.port_entry.insert(0, "3306")
        
        # 用户名
        ttk.Label(self.dialog, text="用户名:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.user_entry = ttk.Entry(self.dialog, width=30)
        self.user_entry.grid(row=2, column=1, padx=10, pady=10)
        self.user_entry.insert(0, "root")
        
        # 密码
        ttk.Label(self.dialog, text="密码:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.password_entry = ttk.Entry(self.dialog, width=30, show="*")
        self.password_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # 数据库名
        ttk.Label(self.dialog, text="数据库:").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        self.database_entry = ttk.Entry(self.dialog, width=30)
        self.database_entry.grid(row=4, column=1, padx=10, pady=10)
        self.database_entry.insert(0, "AcademicWarningSystem")
        
        # 按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="测试连接", command=self.test_connection, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="确定", command=self.save_and_connect, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy, width=12).pack(side=tk.LEFT, padx=5)
    
    def load_current_config(self):
        """加载当前配置"""
        config = self.db_manager.config
        self.host_entry.delete(0, tk.END)
        self.host_entry.insert(0, config.get('host', 'localhost'))
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, str(config.get('port', 3306)))
        self.user_entry.delete(0, tk.END)
        self.user_entry.insert(0, config.get('user', 'root'))
        self.database_entry.delete(0, tk.END)
        self.database_entry.insert(0, config.get('database', 'AcademicWarningSystem'))
    
    def test_connection(self):
        """测试连接"""
        try:
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            user = self.user_entry.get()
            password = self.password_entry.get()
            database = self.database_entry.get()
            
            self.db_manager.set_config(host, port, user, password, database)
            
            if self.db_manager.connect():
                messagebox.showinfo("成功", "数据库连接成功！")
                self.db_manager.disconnect()
            else:
                messagebox.showerror("失败", "数据库连接失败，请检查配置信息")
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字")
        except Exception as e:
            messagebox.showerror("错误", f"连接错误: {str(e)}")
    
    def save_and_connect(self):
        """保存配置并连接"""
        try:
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            user = self.user_entry.get()
            password = self.password_entry.get()
            database = self.database_entry.get()
            
            if not all([host, user, database]):
                messagebox.showerror("错误", "请填写所有必填项")
                return
            
            self.db_manager.set_config(host, port, user, password, database)
            
            if self.db_manager.connect():
                messagebox.showinfo("成功", "数据库连接成功！")
                self.dialog.destroy()
            else:
                messagebox.showerror("失败", "数据库连接失败，请检查配置信息")
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字")
        except Exception as e:
            messagebox.showerror("错误", f"连接错误: {str(e)}")

