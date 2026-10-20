import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# 添加课程的表单
def add_student_form(root, cursor, connection, on_success=None, student_id=None):
    """
    创建一个添加或修改学生信息的表单窗口。

    参数:
    root (tkinter.Tk): 主窗口对象。
    cursor (数据库游标对象): 用于执行数据库操作的游标。
    connection (数据库连接对象): 数据库连接对象。
    on_success (函数, 可选): 当表单提交成功时调用的回调函数。
    student_id (int, 可选): 要修改的学生ID，如果为None则创建新学生。

    返回:
    None
    """
    # 创建一个顶层窗口
    top = tk.Toplevel(root)
    student_gender_var = tk.StringVar(master=top)
    student_name_var = tk.StringVar(master=top)
    student_integral_var = tk.StringVar(master=top)

    student_gender_combobox = ttk.Combobox(top, textvariable=student_gender_var, values=["男", "女"])
    student_gender_combobox.current(0)  # 默认选择第一个选项
    student_gender_combobox.grid(row=1, column=1, padx=10, pady=10)

    if student_id:
        top.title("修改学生信息")
        cursor.execute("SELECT stu_name, stu_gender, stu_integral FROM student WHERE stu_id=?", (student_id,))
        student_data = cursor.fetchall()
        if student_data:
            print(student_data[0][0])
            print(student_data[0][1])
            student_name_var.set(student_data[0][0].strip())  # 直接设置姓名
            if student_data[0][1].strip() == "男":
                student_gender_combobox.current(0)
            else:
                student_gender_combobox.current(1)
            student_integral_var.set(student_data[0][2])
        else:
            messagebox.showwarning("错误", "学生ID不存在")
            top.destroy()  # 如果ID不存在，则关闭窗口

    top.title("添加学生")
    top.geometry("400x200")

    # 创建表单控件
    tk.Label(top, text="学生姓名:").grid(row=0, column=0, padx=10, pady=10)
    teacher_name_entry = tk.Entry(top, textvariable=student_name_var, width=30)
    teacher_name_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(top, text="性别:").grid(row=1, column=0, padx=10, pady=10)

    tk.Label(top, text="积分:").grid(row=2, column=0, padx=10, pady=10)
    student_integral_var.set("0")
    mail_entry = tk.Entry(top, textvariable=student_integral_var, width=30)
    mail_entry.grid(row=2, column=1, padx=10, pady=10)

    # 提交按钮
    def submit():
        """
        提交表单，将学生信息添加到数据库或更新现有学生信息。

        返回:
        None
        """
        student_name = student_name_var.get().strip()
        student_gender = student_gender_var.get().strip()
        student_integral = int(student_integral_var.get().strip())
        if student_name and student_gender:
            if student_id:
                # 调用数据库函数修改教师信息
                if messagebox.askokcancel("确认提交", "您确定要提交修改信息吗？"):
                    try:
                        update_student_in_db(cursor, connection, student_id, student_name, student_gender, student_integral)
                    except Exception as e:
                        messagebox.showerror("错误", f"修改学生信息时出错: {str(e)}")
            else:
                if messagebox.askokcancel("确认提交", "您确定要提交添加信息吗？"):
                    try:
                        add_student_to_db(cursor, connection, student_name, student_gender, student_integral)
                        messagebox.showinfo("成功", "学生信息已添加")
                    except Exception as e:
                        messagebox.showerror("错误", f"添加学生信息时出错: {str(e)}")
            if on_success:
                on_success()
            top.destroy()  # 关闭表单窗口
        else:
            tk.messagebox.showwarning("输入错误", "请填写所有字段")

    submit_btn = tk.Button(top, text="提交", command=submit)
    submit_btn.grid(row=3, column=0, columnspan=2, pady=20)

#向数据库添加学生
def add_student_to_db(cursor,connection,student_name, student_gender,student_integral):
    cursor.execute("INSERT INTO student (stu_name, stu_gender,stu_integral) VALUES (?, ?,?)", (student_name, student_gender, student_integral))
    connection.commit()
    print(f"学生 '{student_name}' 已添加到数据库，性别: {student_gender}") 

#向数据库更新学生信息
def update_student_in_db(cursor,connection,student_id, student_name, student_gender,student_integral):
    cursor.execute("UPDATE student SET stu_name=?, stu_gender=?,stu_integral=? WHERE stu_id=?", (student_name, student_gender, student_integral,student_id))
    connection.commit()
    messagebox.showinfo("成功", "学生信息已修改")