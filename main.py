#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
大学生学业预警与成绩分析系统 - 图形化界面
主程序入口
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from database.db_manager import DatabaseManager

def main():
    """主函数"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()

