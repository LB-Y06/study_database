from tkinter import messagebox, ttk
import tkinter as tk
import add_student
import not_select_tree
import select_tree

class Student:
    columns = ["学生编号","学生姓名","学生性别"]
    tree_dict = {}

    def __init__(self, root, main_frame, cursor,connection):
        self.connection = connection
        self.root = root
        self.main_frame = main_frame
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
            self.tree.column(column, width=50 if column != "学生姓名" else 100, anchor=tk.CENTER)

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
        SELECT * FROM student
        where stu_name like ?
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
            course_id = self.tree_dict[selected_item]
            self.show_detail_window(course_id)

    def show_detail_window(self, student_id):
        detail_window = tk.Toplevel(self.root)
        detail_window.title("学生详细信息")
        detail_window.geometry("1000x800")
        
        buttons_frame = ttk.Frame(detail_window)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X,pady=20)

        for i in range(2):  
           buttons_frame.grid_columnconfigure(i, weight=1)  # 设置每列的权重为1，使其均匀分布

        self.cursor.execute('SELECT * FROM student WHERE stu_id =?', (student_id,))
        student_info=self.cursor.fetchall()
        detail_label = tk.Label(detail_window, text=f"学生编号: {student_info[0][0]}\n学生姓名: {student_info[0][1].strip()}\n学生性别: {student_info[0][2].strip()}\n学生积分: {student_info[0][3]}")
        detail_label.pack(pady=10)

        btn_delete = ttk.Button(buttons_frame, text="删除", command=lambda:self.delete_student(student_id,detail_window))
        btn_delete.grid(row=0, column=0, padx=10, pady=10)

        btn_modify = ttk.Button(buttons_frame, text="修改", command=lambda:self.modify_student(student_id,detail_window))
        btn_modify.grid(row=0, column=1, padx=10, pady=10)

        label_select = tk.Label(detail_window, text="选课：")
        label_select.pack(pady=10)
        not_select_tree.create_treeview(cursor=self.cursor,connection=self.connection,root=detail_window,columns=["课程编号","课程名称","课程学时","课程类别","教师编号","教师姓名"],student_id=student_id)
        label_has_selected = tk.Label(detail_window, text="已选课程：")
        label_has_selected.pack(pady=10)
        select_tree.create_treeview(cursor=self.cursor,connection=self.connection,root=detail_window,columns=["课程编号","课程名称","课程学时","教师姓名","考试成绩"],student_id=student_id)
        
        # 设置窗口的列权重和行权重，使组件能够根据需要扩展
        detail_window.grid_columnconfigure(0, weight=1)  # 第一列权重设为1，表示可以扩展
        detail_window.grid_columnconfigure(1, weight=3)  # 第二列权重设为3，表示比第一列更宽
        detail_window.grid_rowconfigure(0, weight=1)    # 第一行权重设为1，表示可以扩展
        detail_window.grid_rowconfigure(1, weight=1)    # 第二行权重设为1，与第一行相同



    def delete_student(self,student_id,detail_window):
        if messagebox.askyesno("删除学生", "确认删除学生吗？"):
            try:
                self.cursor.execute('DELETE FROM student WHERE stu_id =?', (student_id,))
                self.connection.commit()
                detail_window.destroy()
                messagebox.showinfo("删除成功", "学生已成功删除。")
                self.refresh_display()
            except Exception as e:
                messagebox.showerror("错误", f"删除学生时出错: {str(e)}")
    
    def modify_student(self,student_id,detail_window):
        detail_window.destroy()
        add_student.add_student_form(root=self.root,cursor=self.cursor,connection=self.connection,student_id=student_id,on_success=self.refresh_display)

    def refresh_display(self):
        self.populate_treeview(self.search_var.get())


        
