import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
COURSE_TYPES = ["软件开发与工程","计算机系统结构","数学","思政","英语","物理","美育","算法","编程语言","体育","学科交叉"]


def add_course_form(root, cursor, connection, on_success=None, course_id=None):
    """
    创建一个表单，用于添加或修改课程信息。

    参数:
    root: 主窗口对象。
    cursor: 数据库游标对象。
    connection: 数据库连接对象。
    on_success: 成功提交后的回调函数。
    course_id: 要修改的课程ID，如果为None则表示添加新课程。

    返回:
    无
    """
    # 查询所有教师信息
    result = cursor.execute("SELECT tutor_id, tutor_name FROM teacher")
    result = result.fetchall()
    teachers = []
    for i in result:
        teachers.append(str(i[0]).strip() + " " + str(i[1]).strip())

    # 创建一个顶层窗口
    top = tk.Toplevel(root)

    # 创建变量来存储课程名称、类型、学时和教师信息
    course_name_var = tk.StringVar(master=top)
    course_type_var = tk.StringVar(master=top)
    hours_var = tk.IntVar(master=top)
    course_type_var = tk.StringVar(master=top)
    course_teacher_var = tk.StringVar(master=top)

    # 创建课程类型下拉框
    course_type_combobox = ttk.Combobox(top, textvariable=course_type_var, values=COURSE_TYPES)
    # 创建教师下拉框
    teacher_combobox = ttk.Combobox(top, textvariable=course_teacher_var, values=teachers)

    # 如果 course_id 存在，则表示修改课程信息
    if course_id:
        top.title("修改课程信息")
        # 从数据库中查询课程信息
        cursor.execute("SELECT cour_name, cour_kind, cour_hour FROM course WHERE cour_id=?", (course_id,))
        course_data = cursor.fetchall()
        if course_data:
            # 设置课程名称、类型和学时
            course_name_var.set(course_data[0][0].strip())
            course_type_var.set(course_data[0][1].strip())
            hours_var.set(str(course_data[0][2]).strip())
        # 从数据库中查询授课教师信息
        cursor.execute("SELECT tutor_id FROM lectures WHERE cour_id=?", (course_id,))
        course_teacher_id = cursor.fetchall()
        course_teacher_id = int(course_teacher_id[0][0].strip())
        # 从数据库中查询教师姓名
        cursor.execute("SELECT tutor_name FROM teacher WHERE tutor_id=?", (course_teacher_id,))
        course_teacher_name = cursor.fetchall()
        course_teacher_name = course_teacher_name[0][0].strip()
        # 设置教师信息
        course_teacher_var.set(str(course_teacher_id) + " " + course_teacher_name)
    else:
        top.title("添加课程")

    top.geometry("400x300")

    # 创建课程名称标签和输入框
    tk.Label(top, text="课程名称:").grid(row=0, column=0, padx=10, pady=10)
    course_name_entry = tk.Entry(top, textvariable=course_name_var, width=30)
    course_name_entry.grid(row=0, column=1, padx=10, pady=10)

    # 创建学时标签和输入框
    tk.Label(top, text="学时:").grid(row=1, column=0, padx=10, pady=10)
    hours_entry = tk.Entry(top, textvariable=hours_var, width=10)
    hours_entry.grid(row=1, column=1, padx=10, pady=10)

    # 创建课程类型标签和下拉框
    tk.Label(top, text="课程类型:").grid(row=2, column=0, padx=10, pady=10)
    course_type_combobox.grid(row=2, column=1, padx=10, pady=10)

    # 创建教师标签和下拉框
    tk.Label(top, text="教师:").grid(row=3, column=0, padx=10, pady=10)
    teacher_combobox.grid(row=3, column=1, padx=10, pady=10)

    # 提交按钮的回调函数
    def submit():
        # 获取表单中的数据
        course_name = course_name_var.get()
        hours = hours_var.get()
        course_type = course_type_var.get()
        teacher = course_teacher_var.get()
        teacher_id = teacher.split(" ")[0]
        # 检查数据是否完整
        if course_name and hours and course_type:
            # 如果是修改课程信息
            if course_id:
                # 弹出确认对话框
                if messagebox.askokcancel("确认提交", "您确定要提交修改信息吗？"):
                    try:
                        # 更新数据库中的课程信息
                        update_course_in_db(cursor, connection, course_id, course_name, hours, course_type, teacher_id)
                    except Exception as e:
                        # 显示错误信息
                        messagebox.showerror("错误", f"修改课程信息时出错: {str(e)}")
            else:
                # 弹出确认对话框
                if messagebox.askokcancel("确认提交", "您确定要提交添加信息吗？"):
                    try:
                        # 向数据库中添加新课程信息
                        add_course_to_db(cursor, connection, course_name, hours, course_type, teacher_id)
                    except Exception as e:
                        # 显示错误信息
                        messagebox.showerror("错误", f"添加课程时出错: {str(e)}")
            # 如果有回调函数，则调用回调函数
            if on_success:
                on_success()
            # 关闭表单窗口
            top.destroy()
        else:
            # 显示警告信息
            tk.messagebox.showwarning("输入错误", "请填写所有字段")

    # 创建提交按钮
    submit_btn = tk.Button(top, text="提交", command=submit)
    submit_btn.grid(row=4, column=0, columnspan=2, pady=20)

# 假设的数据库添加函数（需要您根据实际的数据库结构来实现）
def add_course_to_db(cursor, connection, course_name, hours, course_type, teacher_id):
    """
    向数据库中添加一门新课程。

    参数:
    cursor: 数据库游标对象。
    connection: 数据库连接对象。
    course_name: 课程名称。
    hours: 学时。
    course_type: 课程类型。
    teacher_id: 教师ID。

    返回:
    无
    """
    try:
        # 向课程表中插入新课程信息
        cursor.execute("INSERT INTO course (cour_name, cour_hour, cour_kind) "
                       "VALUES (?, ?, ?)", (course_name, hours, course_type))
        connection.commit()

        # 获取新插入课程的ID
        cursor.execute("select IDENT_CURRENT( 'course' )")
        last_id_tuple = cursor.fetchone()

        if last_id_tuple:
            # 从元组中提取ID
            last_id = last_id_tuple[0]

            # 向授课表中插入教师信息
            cursor.execute("INSERT INTO lectures (cour_id, tutor_id) VALUES (?, ?)", (last_id, teacher_id))
            connection.commit()
        else:
            print("未能获取到课程 ID，请检查数据库和表结构。")
    except Exception as e:
        # 发生异常时回滚事务
        connection.rollback()
        # 打印错误信息
        print(f"添加课程时出错: {e}")


def update_course_in_db(cursor, connection, course_id, course_name, hours, course_type, teacher_id):
    """
    更新数据库中的课程信息。

    参数:
    cursor: 数据库游标对象。
    connection: 数据库连接对象。
    course_id: 要更新的课程ID。
    course_name: 更新后的课程名称。
    hours: 更新后的学时。
    course_type: 更新后的课程类型。
    teacher_id: 更新后的教师ID。

    返回:
    无
    """
    try:
        # 更新课程表中的课程信息
        cursor.execute("UPDATE course SET cour_name=?, cour_hour=?, cour_kind=? WHERE cour_id=?",
                       (course_name, hours, course_type, course_id))
        connection.commit()

        # 更新授课表中的教师信息
        cursor.execute("UPDATE lectures SET tutor_id=? WHERE cour_id=?", (teacher_id, course_id))
        connection.commit()

        # 显示成功信息
        messagebox.showinfo("成功", "课程信息已修改")
    except Exception as e:
        # 发生异常时回滚事务
        connection.rollback()
        # 打印错误信息
        print(f"修改课程时出错: {e}")


    