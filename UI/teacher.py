from tkinter import messagebox, ttk
import tkinter as tk

from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
import add_teacher
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Teacher:
    columns = ["教师编号","教师姓名","教师性别","教师邮箱"]
    tree_dict = {}
    tree_dict_course = {}

    def __init__(self, root, main_frame, cursor,connection):
        self.root = root
        self.main_frame = main_frame
        self.connection = connection
        self.cursor = cursor
        self.frame = ttk.Frame(self.main_frame)
        self.frame.pack(fill=tk.X, padx=10, pady=10)
        self.tree = ttk.Treeview(self.frame, columns=self.columns, show='headings')

        # 创建搜索框和搜索按钮
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.frame, textvariable=self.search_var, width=30)
        self.btn_search = ttk.Button(self.frame, text="搜索", command=self.refresh_display)
        # 将搜索框和搜索按钮放置在Frame中
        self.search_entry.pack(side=tk.LEFT, padx=10, pady=10)


        self.create_treeview()

    def create_treeview(self):
        # 定义列标题和它们的宽度
        for column in self.columns:
            self.tree.heading(column, text=column, anchor=tk.CENTER)
            self.tree.column(column, width=50 if column != "教师姓名" else 100, anchor=tk.CENTER)

        # 从数据库获取课程数据
        self.populate_treeview()
        # 绑定Treeview的<<TreeviewSelect>>事件到处理函数

        # 绑定Treeview的<<TreeviewSelect>>事件到处理函数
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # 放置Treeview
        self.search_entry.pack(side=tk.TOP, padx=10, pady=5)
        self.btn_search.pack(side=tk.TOP, padx=10, pady=5)
        self.tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        return self.frame

    def populate_treeview(self,search_term=""):
        query = '''
        SELECT * FROM teacher
        where tutor_name like ?
        '''
        search_term = f"%{search_term}%"
        self.cursor.execute(query, (search_term,))
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
            teacher_id = self.tree_dict[selected_item]
            self.show_detail_window(teacher_id)
    
    def on_tree_select_course(self, event):
        tree_course = event.widget
        selected_item = tree_course.focus()
        if selected_item in self.tree_dict_course:
            course_id = self.tree_dict_course[selected_item]
            self.show_detail_window_course(course_id)

    def show_detail_window(self, teacher_id):
        detail_window = tk.Toplevel(self.root)
        detail_window.title("教师详细信息")
        detail_window.geometry("1000x800")
        buttons_frame = ttk.Frame(detail_window)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)

        for i in range(2):  
           buttons_frame.grid_columnconfigure(i, weight=1)  # 设置每列的权重为1，使其均匀分布

        self.cursor.execute('SELECT * FROM teacher WHERE tutor_id =?', (teacher_id,))
        teacher_info=self.cursor.fetchall()
        detail_label = tk.Label(detail_window, text=f"教师编号: {teacher_info[0][0]}\n教师姓名: {teacher_info[0][1].strip()}\n教师性别: {teacher_info[0][2].strip()}\n教师邮箱: {str(teacher_info[0][3]).strip()}")
        detail_label.pack(pady=10)

        self.cursor.execute("SELECT * FROM course where cour_id in (SELECT cour_id FROM lectures WHERE tutor_id =?)", (teacher_id,))
        courses=self.cursor.fetchall()
        detail_label = tk.Label(detail_window, text="教授的课程：")
        detail_label.pack(pady=10)
        columns = ["课程编号", "课程名称", "课程学时", "课程种类"]
        tree_course = ttk.Treeview(detail_window, columns=columns, show="headings")
        for column in columns:
            tree_course.heading(column, text=column, anchor=tk.CENTER)
            tree_course.column(column, width=50 if column != "课程名称" else 100, anchor=tk.CENTER)
        tree_course.bind("<<TreeviewSelect>>", self.on_tree_select_course)
        tree_course.pack(fill=tk.BOTH, expand=True)
        if courses:
            for row in courses:
                    info = [str(column).strip() for column in row]
                    iid = tree_course.insert("", "end", values=info, tags=(info[0],))
                    self.tree_dict_course[iid] = info[0]
        

        btn_delete = ttk.Button(buttons_frame, text="删除", command=lambda:self.delete_teacher(teacher_id,detail_window))
        btn_delete.grid(row=0, column=0, padx=10, pady=10)

        btn_modify = ttk.Button(buttons_frame, text="修改", command=lambda:self.modify_teacher(teacher_id,detail_window))
        btn_modify.grid(row=0, column=1, padx=10, pady=10)


    def refresh_display(self):
        self.populate_treeview(self.search_var.get())

    def delete_teacher(self,teacher_id,detail_window):
          if messagebox.askokcancel("确认删除", "您确定要删除这位教师的信息吗？"):
            try:
                self.cursor.execute("DELETE FROM teacher WHERE tutor_id = ?", (teacher_id,))
                self.connection.commit()
                messagebox.showinfo("删除成功", "教师信息已成功删除。")
                detail_window.destroy()
                self.refresh_display()  # 假设这是刷新显示的方法
            except Exception as e:
                messagebox.showerror("删除失败", f"删除教师信息时出错: {e}")

    def modify_teacher(self,teacher_id,detail_window):
        add_teacher.add_teacher_form(self.root,self.cursor,self.connection,on_success=self.refresh_display,teacher_id=teacher_id)
        detail_window.destroy()
    
    def show_detail_window_course(self, course_id):
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
        # 假设这是您提供的数据

        # 遍历数据并提取信息
        for course in data:
            cour_id, cour_name, cour_hour, cour_kind, selected_count, completed_count, grades_list, average_score = course
            
            if grades_list:
                grades = [int(grade) for grade in grades_list.split(',')]
                average_grade = "{:.1f}".format(sum(grades) / len(grades))
            else:
                grades = []
                average_grade = None
            
                

        detail_label = tk.Label(detail_window, text=f"课程编号: {str(cour_id)}\n课程名称: {str(cour_name).strip()}\n课程时长: {str(cour_hour).strip()}\n课程种类: {str(cour_kind).strip()}\n选择人数: {str(selected_count).strip()}\n完成人数: {str(completed_count).strip()}\n平均成绩: {str(average_grade).strip()}\n平均评分: {str(average_score).strip()}")

        detail_label.pack(pady=10)
        detail_label.configure(font=("SimSun", 12))
            # 在Matplotlib中设置字体
        plt.rcParams['font.sans-serif'] = ['SimSun']  # 设置默认字体为宋体
        plt.rcParams['axes.unicode_minus'] = False  # 确保负号显示正常

        tk.Label(detail_window, text="成绩分布:").pack(pady=5)
        if grades is None:
            tk.Label(detail_window, text="暂无成绩").pack()
        else:
            print(grades)
            fig, ax = plt.subplots()
            ax.hist(grades, bins=range(0, 110, 10), edgecolor='black')
            ax.yaxis.set_major_locator(MultipleLocator(1))
            ax.set_xlabel("分数")
            ax.set_ylabel("人数")
            # 将 Matplotlib 图形嵌入到 Tkinter 窗口
            canvas = FigureCanvasTkAgg(fig, master=detail_window)
            canvas.draw()
            canvas.get_tk_widget().pack()

