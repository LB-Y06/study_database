from tkinter import Entry, StringVar, messagebox,ttk
import tkinter as tk

from matplotlib.ticker import MultipleLocator

import add_course
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class Course:
    columns = ["课程编号", "课程名称", "课程学时", "课程类别","教师编号","教师姓名"]
    tree_dict = {}


    def __init__(self, root, main_frame, cursor,connection):
        self.connection = connection
        self.root = root
        self.main_frame = main_frame
        self.cursor = cursor
        self.frame = tk.Frame(self.main_frame)
        self.frame.pack(fill=tk.X, padx=10, pady=10)
        self.tree = ttk.Treeview(self.frame, columns=self.columns, show='headings')
        self.search_var = StringVar()  # 用于存储搜索关键词
        self.search_entry = Entry(self.frame, textvariable=self.search_var, width=30)  # 搜索输入框
        self.btn_search = ttk.Button(self.frame, text="查询", command=self.refresh_display)  # 查询按钮
        self.create_treeview()

    def create_treeview(self):
        # 定义列标题和它们的宽度
        for column in self.columns:
            self.tree.heading(column, text=column, anchor=tk.CENTER)
            self.tree.column(column, width=50 if column != "课程名称" else 100, anchor=tk.CENTER)

        # 从数据库获取课程数据

        self.populate_treeview()

        # 绑定Treeview的<<TreeviewSelect>>事件到处理函数
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # 放置Treeview
        self.search_entry.pack(side=tk.TOP, padx=10, pady=5)
        self.btn_search.pack(side=tk.TOP, padx=10, pady=5)
        self.tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        return self.frame

    def populate_treeview(self,search_term=""):
        query = '''
        SELECT 
            course.cour_id, 
            course.cour_name, 
            course.cour_hour, 
            course.cour_kind, 
            teacher.tutor_id,
            teacher.tutor_name
        FROM 
            course
        INNER JOIN 
            lectures ON course.cour_id = lectures.cour_id
        INNER JOIN 
            teacher ON teacher.tutor_id = lectures.tutor_id
        WHERE 
            course.cour_name LIKE ? OR teacher.tutor_name LIKE ?
        '''
        search_term = f"%{search_term}%"
        self.cursor.execute(query, (search_term, search_term))
        courses = self.cursor.fetchall()
        

        self.tree.delete(*self.tree.get_children())  # 清空现有的条目

        if courses:
            for row in courses:
                info = [str(column).strip() for column in row]
                iid = self.tree.insert("", "end", values=info, tags=(info[0],))
                self.tree_dict[iid] = info[0]

    def on_tree_select(self, event):
        tree = event.widget
        selected_item = tree.focus()
        if selected_item in self.tree_dict:
            course_id = self.tree_dict[selected_item]
            self.show_detail_window(course_id)

    def show_detail_window(self, course_id):
        detail_window = tk.Toplevel(self.root)
        detail_window.title("课程详细信息")
        detail_window.geometry("800x600")

        buttons_frame = tk.Frame(detail_window)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)

        for i in range(2):  
           buttons_frame.grid_columnconfigure(i, weight=1)  # 设置每列的权重为1，使其均匀分布

        self.cursor.execute('''WITH CourseSelections AS (
                    SELECT 
                        cs.cour_id,
                        COUNT(DISTINCT cs.stu_id) AS selected_count, -- 选择该课程的不同学生人数
                        SUM(CASE WHEN cs.degree_of_completion = '100%' THEN 1 ELSE 0 END) AS completed_count, -- 完成该课程的人数（假设'100%'表示完成）
                        STRING_AGG(cs.grades, ',') WITHIN GROUP (ORDER BY cs.stu_id) AS grades_list, -- 该课程的非空成绩列表（逗号分隔），按学生ID排序
                        SUM(CASE WHEN cs.score IS NOT NULL THEN 1 ELSE 0 END) AS scored_count, -- 已评分的学生人数
                        AVG(cs.score) AS average_score -- 评分平均分，仅包括非NULL评分
                    FROM 
                        [OLPMS].[dbo].[courseSelection] cs
                    GROUP BY 
                        cs.cour_id
                )
                SELECT 
                    c.cour_id,
                    c.cour_name,
                    c.cour_hour,
                    c.cour_kind,
                    ISNULL(cs.selected_count, 0) AS selected_count, -- 如果没有学生选择该课程，则显示为0
                    ISNULL(cs.completed_count, 0) AS completed_count, -- 如果没有学生完成该课程，则显示为0
                    ISNULL(cs.grades_list, '') AS grades_list, -- 如果没有成绩，则显示为空字符串
                    CASE 
                        WHEN cs.scored_count > 0 THEN cs.average_score -- 如果有评分，则显示平均分
                        ELSE NULL -- 如果没有评分，则显示为NULL（或您可以选择显示0或其他值）
                    END AS average_score
                FROM 
                    [OLPMS].[dbo].[course] c
                LEFT JOIN 
                    CourseSelections cs
                ON 
                    c.cour_id = cs.cour_id
                where c.cour_id=?
                ORDER BY 
                    c.cour_id;''' ,(course_id,))
        data=self.cursor.fetchall()

        # 遍历数据并提取信息
        for course in data:
            cour_id, cour_name, cour_hour, cour_kind, selected_count, completed_count, grades_list, average_score = course
            
            if grades_list:
                grades = [int(grade) for grade in grades_list.split(',')]
                average_grade = sum(grades) / len(grades)
                formatted_average = "{:.1f}".format(average_grade).strip()
            else:
                grades = []
                formatted_average=None
            
                

        detail_label = tk.Label(detail_window, text=f"课程编号: {str(cour_id)}\n课程名称: {str(cour_name).strip()}\n课程时长: {str(cour_hour).strip()}\n课程种类: {str(cour_kind).strip()}\n选择人数: {str(selected_count).strip()}\n完成人数: {str(completed_count).strip()}\n平均成绩: {str(formatted_average)}\n平均评分: {str(average_score).strip()}")

        detail_label.pack(pady=10)
        detail_label.configure(font=("SimSun", 12))
            # 在Matplotlib中设置字体
        plt.rcParams['font.sans-serif'] = ['SimSun']  # 设置默认字体为宋体
        plt.rcParams['axes.unicode_minus'] = False  # 确保负号显示正常

        tk.Label(detail_window, text="成绩分布:").pack(pady=5)
        if grades is None:
            tk.Label(detail_window, text="暂无成绩").pack()
        else:
            fig, ax = plt.subplots()
            ax.hist(grades, bins=range(0, 110, 10), edgecolor='black')
            ax.yaxis.set_major_locator(MultipleLocator(1))
            ax.set_xlabel("分数")
            ax.set_ylabel("人数")
            # 将 Matplotlib 图形嵌入到 Tkinter 窗口
            canvas = FigureCanvasTkAgg(fig, master=detail_window)
            canvas.draw()
            canvas.get_tk_widget().pack()

        btn_delete = tk.Button(buttons_frame, text="删除", command=lambda:self.delete_course(course_id,detail_window))
        btn_delete.grid(row=0, column=0, padx=10, pady=10)

        btn_modify = tk.Button(buttons_frame, text="修改", command=lambda:self.modify_course(course_id,detail_window))
        btn_modify.grid(row=0, column=1, padx=10, pady=10)

    def delete_course(self, course_id,detail_window):
        if messagebox.askyesno("确认", "确定要删除该课程吗？"):
            try:
                self.cursor.execute('DELETE FROM course WHERE cour_id=?', (course_id,))
                self.connection.commit()
                detail_window.destroy()
                self.refresh_display()
                messagebox.showinfo("成功", "课程已删除")
            except Exception as e:
                messagebox.showerror("错误", f"删除课程时出错: {str(e)}")
    
    def modify_course(self, course_id,detail_window):
        detail_window.destroy()
        add_course.add_course_form(self.root, self.cursor, self.connection, course_id=course_id,on_success=self.refresh_display)
        


    def refresh_display(self):
        self.populate_treeview(self.search_var.get())


        
