import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import askyesno

def create_treeview(cursor,connection,root, columns,student_id):
    frame = tk.Frame(root)
    
    # 创建Treeview对象，并设置show为'headings'以显示列标题
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    tree.delete(*tree.get_children())
    for col in columns:
        tree.heading(col, text=col)  # 设置列标题
    
    for i in range(6):  # 假设您有6个按钮，因此有6列
        frame.grid_columnconfigure(i, weight=1)  # 设置每列的权重为1，使其均匀分布
    
    def get_data(cursor,student_id):
        cursor.execute('''
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
            NOT EXISTS (
                SELECT 1
                FROM courseSelection
                WHERE courseSelection.stu_id = ? AND courseSelection.cour_id = course.cour_id
            )
        ''',(student_id,))
        data = cursor.fetchall()
        b = []
        
        for row in data:
            # 创建一个新的列表来存储处理后的元素
            new_row = []
            for column in row:
                if isinstance(column, str):
                    # 去除字符串的前后空格，并将处理后的字符串添加到新列表中
                    new_row.append(column.strip())
                else:
                    # 如果不是字符串，则直接添加到新列表中
                    new_row.append(column)
            # 将处理后的新列表添加到b中
            b.append(tuple(new_row))  # 注意这里使用了tuple()来创建一个元组
        
        # 替换原始的data列表
        data = b
        return data

    
    data=get_data(cursor=cursor,student_id=student_id)
            

    frame.pack(fill=tk.X, padx=10, pady=10)
    tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    tree_dict = {}

    for item in data:
        iid = tree.insert("", "end", values=item, tags=(item[0],))
        tree_dict[iid] = item[0]  # 假设第一列是ID或唯一标识符


    

    def on_tree_select(event):
        selected_item = tree.focus()  # 获取当前选中的条目
        if selected_item in tree_dict:
            id = tree_dict[selected_item]
            show_detail_window(cursor=cursor,connection=connection,root=root,course_id=id,student_id=student_id, item_data=data[tree.index(selected_item)],tree=tree)
    
    tree.bind("<<TreeviewSelect>>", on_tree_select)


        # 在Treeview创建后绑定事件
    
    
    def show_detail_window(cursor,connection,root,course_id,student_id, item_data,tree):
        detail_window = tk.Toplevel(root)
        detail_window.title("课程信息")
        detail_window.geometry("500x400")
        # 这里可以根据item_data显示更多详细信息
        # 例如，使用多行标签或网格布局
        label_text = f"课程编号: {item_data[0]}\n课程名称: {item_data[1]}\n课程时长: {item_data[2]}\n课程种类: {item_data[3]}\n教师编号: {item_data[4]}\n教师姓名: {item_data[5]}"
        label = tk.Label(detail_window, text=label_text)
        label.pack()
        btn_select = ttk.Button(detail_window, text="选择")
        btn_select.config(command=lambda:select_course(cursor,connection=connection,detail_windows=detail_window,course_id=course_id,student_id=student_id,tree=tree))
        btn_select.pack()

    def select_course(cursor,connection,detail_windows,course_id,student_id,tree):
        if messagebox.askyesno("选择", "是否选择该课程"):
            detail_windows.destroy()
            root.destroy()
            default_completion = '0%'
            cursor.execute("INSERT INTO courseSelection (stu_id, cour_id,degree_of_completion) VALUES (?, ?,?)", (student_id, course_id, default_completion))

            connection.commit()
            messagebox.showinfo("选择成功", "选择成功")

    

        




        




