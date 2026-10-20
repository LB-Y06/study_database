import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# 添加课程的表单
def add_teacher_form(root, cursor, connection, on_success=None, teacher_id=None,detail_window=None):    
    # 创建一个顶层窗口
    top = tk.Toplevel(root)
    teacher_name_var = tk.StringVar(master=top)
    teacher_gender_var = tk.StringVar(master=top)
    teacher_mail_var = tk.StringVar(master=top)

    teacher_gender_combobox = ttk.Combobox(top, textvariable=teacher_gender_var, values=["男", "女"])
    teacher_gender_combobox.grid(row=1, column=1, padx=10, pady=10)

    if teacher_id:
        top.title("修改教师信息")
        cursor.execute("SELECT tutor_name, tutor_gender, tutor_mail FROM teacher WHERE tutor_id=?", (teacher_id,))
        teacher_data=cursor.fetchall()
        if teacher_data:
            teacher_name_var.set(teacher_data[0][0].strip())  # 直接设置姓名
            if teacher_data[0][1].strip() == "男":
                teacher_gender_combobox.current(0)
            else:
                teacher_gender_combobox.current(1)
            teacher_mail_var.set(teacher_data[0][2])  # 设置邮箱
        else:
            messagebox.showwarning("错误", "教师ID不存在")
            top.destroy()  # 如果ID不存在，则关闭窗口
    else:
        top.title("添加教师")
        teacher_gender_combobox.current(0)  # 默认选择第一个选项
    top.geometry("400x200")

    # 创建表单控件
    tk.Label(top, text="教师姓名:").grid(row=0, column=0, padx=10, pady=10)
    teacher_name_entry = ttk.Entry(top, textvariable=teacher_name_var, width=30)
    teacher_name_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(top, text="性别:").grid(row=1, column=0, padx=10, pady=10)


    tk.Label(top, text="邮箱(可选):").grid(row=2, column=0, padx=10, pady=10)
    mail_entry = ttk.Entry(top, textvariable=teacher_mail_var, width=30)
    mail_entry.grid(row=2, column=1, padx=10, pady=10)

    # 提交按钮
    def submit(detail_window=None):
        teacher_name = teacher_name_var.get().strip()
        teacher_gender = teacher_gender_var.get().strip()
        teacher_mail = teacher_mail_var.get().strip()
        if teacher_name and teacher_gender:
            if teacher_id:
                update_teacher(cursor, connection, teacher_id, teacher_name, teacher_gender, teacher_mail,detail_window=detail_window)
                top.destroy()  # 关闭表单窗口
            else:
                add_teacher_to_db(cursor, connection, teacher_name, teacher_gender, teacher_mail)
                top.destroy()  # 关闭表单窗口
            
            if on_success:
                on_success()
        else:
            messagebox.showwarning("输入错误", "请填写所有字段")

    submit_btn = ttk.Button(top, text="提交", command=lambda:submit(detail_window=detail_window))
    submit_btn.grid(row=4, column=0, columnspan=2, pady=20)

def update_teacher(cursor, connection, teacher_id, new_name, new_gender, new_mail,detail_window=None):
    if messagebox.askokcancel("确认提交", "您确定要提交修改信息吗？"):
        try:
            cursor.execute("UPDATE teacher SET tutor_name=?, tutor_gender=?, tutor_mail=? WHERE tutor_id=?", (new_name, new_gender, new_mail, teacher_id))
            connection.commit()
            messagebox.showinfo("修改成功", "教师信息已成功修改。")
            if detail_window:
                detail_window.destroy()  # 关闭详情窗口
        except Exception as e:
            messagebox.showerror("删除失败", f"删除教师信息时出错: {e}")

#更新教师
def add_teacher_to_db(cursor, connection, teacher_name, teacher_gender, teacher_mail):
    cursor.execute("INSERT INTO teacher (tutor_name, tutor_gender, tutor_mail) VALUES (?, ?, ?)", (teacher_name, teacher_gender, teacher_mail))
    connection.commit()
    messagebox.showinfo("添加成功", "教师信息已成功添加。")