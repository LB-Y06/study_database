import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox



def create_treeview(cursor,connection,root, columns,student_id):
    frame = tk.Frame(root)
    
    # 创建Treeview对象，并设置show为'headings'以显示列标题
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    tree.delete(*tree.get_children())
    for col in columns:
        tree.heading(col, text=col)  # 设置列标题
    
    for i in range(6):
        frame.grid_columnconfigure(i, weight=1)
    
        def get_data(cursor,student_id):
            cursor.execute('''
            SELECT 
                course.cour_id, 
                course.cour_name, 
                course.cour_hour, 
                course.cour_kind, 
                teacher.tutor_id,
                teacher.tutor_name,
                courseSelection.grades  -- 添加成绩字段
            FROM 
                course
            INNER JOIN 
                lectures ON course.cour_id = lectures.cour_id
            INNER JOIN 
                teacher ON teacher.tutor_id = lectures.tutor_id
            INNER JOIN 
                courseSelection ON courseSelection.cour_id = course.cour_id AND courseSelection.stu_id = ?  -- 直接连接courseSelection表
            ''', (student_id,))
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
    
    data=get_data(cursor=cursor,student_id=student_id)#获取数据
            

    frame.pack(fill=tk.BOTH, padx=10, pady=10)
    tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)

    tree_dict = {}

    for item in data:
        iid = tree.insert("", "end", values=[item[0],item[1],item[2],item[5],item[6]], tags=(item[0],))
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
        cursor.execute("SELECT grades,degree_of_completion,score FROM courseSelection WHERE stu_id=? AND cour_id=?",(student_id,course_id))
        data=cursor.fetchall()
        label_text = f"课程编号: {item_data[0]}\n课程名称: {item_data[1]}\n课程时长: {item_data[2]}\n课程种类: {item_data[3]}\n教师编号: {item_data[4]}\n教师姓名: {item_data[5]}\n成绩: {data[0][0]}\n学习进度: {data[0][1].strip()}\n对课程的评价: {data[0][2]}"
        label = tk.Label(detail_window, text=label_text)
        label.pack()

        course_hours=item_data[2]
        degree_of_completion=data[0][1].strip()
        degree_of_completion=float(degree_of_completion.replace(' ', '').strip('%')) / 100


        

        btn_study = ttk.Button(detail_window, text="开始学习")
        btn_test = ttk.Button(detail_window, text="开始测试")
        btn_drop = ttk.Button(detail_window, text="退课")
        btn_score=ttk.Button(detail_window,text="评分")

        btn_study.pack()
        btn_test.pack()
        btn_drop.pack()
        btn_score.pack()

        if degree_of_completion>0.3:
            btn_drop.config(state=tk.DISABLED)
        if degree_of_completion<0.9:
            btn_test.config(state=tk.DISABLED)
            btn_score.config(state=tk.DISABLED)
        if data[0][0]!=None:
            btn_test.config(state=tk.DISABLED)


        btn_study.config(command=lambda:ask_study_time(degree_of_completion))
        btn_test.config(command=lambda:test())
        btn_drop.config(command=lambda:drop())
        btn_score.config(command=lambda:score())

        def score():
            score=random.randint(50,100)
            messagebox.showinfo("提示", f"对改课的评分为{score}")
            cursor.execute("UPDATE courseSelection SET score=? WHERE stu_id=? AND cour_id=?",(score,student_id,course_id))
            connection.commit()
            detail_window.destroy()
            root.destroy()

        def test():
            grade=random.randint(50,100)
            messagebox.showinfo("提示", f"你的成绩为{grade}")
            cursor.execute("UPDATE courseSelection SET grades=? WHERE stu_id=? AND cour_id=?",(grade,student_id,course_id))
            connection.commit()
            detail_window.destroy()
            root.destroy()
        
        def drop():
            if messagebox.askyesno("确认退课", "您确定要退课吗？"):
                cursor.execute("DELETE FROM courseSelection WHERE stu_id=? AND cour_id=?",(student_id,course_id))
                connection.commit()
                messagebox.showinfo("提示", "退课成功")
                detail_window.destroy()
                root.destroy()

        def ask_study_time(degree_of_completion):
            # 创建一个Toplevel窗口
            input_dialog = tk.Toplevel(detail_window)
            input_dialog.title("输入学习时间")
            # 设置窗口大小
            input_dialog.geometry("200x160")
            # 创建标签和输入框
            label = ttk.Label(input_dialog, text="请输入学习时间（小时）：")
            label.pack(pady=10)
        
            entry_var = tk.StringVar()
            entry = tk.Entry(input_dialog, textvariable=entry_var)
            entry.pack(pady=5)
        
            # 定义提交按钮的回调函数
            def on_submit(degree_of_completion):
                study_time = entry_var.get()
                study_time=float(study_time)

                study_time="{:.3f}".format((study_time+degree_of_completion*course_hours)/course_hours)
                study_time=float(study_time.strip())
                if study_time>=1:
                    degree_of_completion="100%"
                else:
                    degree_of_completion=str(study_time*100)+"%"
                cursor.execute("UPDATE courseSelection SET degree_of_completion=? WHERE stu_id=? AND cour_id=?",(degree_of_completion,student_id,course_id))
                connection.commit()
                messagebox.showinfo("提示", f"太厉害，你已完成该课程的{degree_of_completion}")
                # 关闭对话框
                input_dialog.destroy()
                detail_window.destroy()
                root.destroy()
                # 这里可以添加额外的处理逻辑，比如验证输入值
        
            # 创建提交按钮
            submit_button = tk.Button(input_dialog, text="提交", command=lambda:on_submit(degree_of_completion))
            submit_button.pack(pady=10)

                        
        





        

