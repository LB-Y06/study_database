import tkinter as tk
import connectSQL as sql
import add_course
import add_teacher
import add_student
import course
import teacher
import student

# 创建主窗口
root = tk.Tk()
root.title("线上学习管理系统")
root.geometry("1000x1000")




cursor = sql.cursor
connection=sql.connection

# 创建框架来容纳按钮和标签
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

course=course.Course(root,main_frame,cursor,connection)
teacher=teacher.Teacher(root,main_frame,cursor,connection)
student=student.Student(root,main_frame,cursor,connection)

# 创建三个标签来模拟不同的页面
page_course = course.create_treeview()
page_teacher = teacher.create_treeview()
page_student = student.create_treeview()

buttons_frame = tk.Frame(main_frame)
buttons_frame.pack(side=tk.TOP, fill=tk.X)
page_course.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
page_teacher.pack_forget()  # 隐藏页面2
page_student.pack_forget()  # 隐藏页面3

# 按钮的回调函数，用于切换页面
def show_page_course():
    page_course.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    page_teacher.pack_forget()
    page_student.pack_forget()

def show_page_teacher():
    page_course.pack_forget()
    page_teacher.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    page_student.pack_forget()

def show_page_student():
    page_course.pack_forget()
    page_teacher.pack_forget()
    page_student.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# 创建并排的按钮

def refresh_course_page():
    # 假设 page_course 有一个方法来刷新其显示的内容
    course.refresh_display()

def refresh_teacher_page():
    # 假设 page_teacher 有一个方法来刷新其显示的内容
    teacher.refresh_display()

def refresh_student_page():
    # 假设 page_student 有一个方法来刷新其显示的内容
    student.refresh_display()


for i in range(6):  # 假设您有6个按钮，因此有6列
    buttons_frame.grid_columnconfigure(i, weight=1)  # 设置每列的权重为1，使其均匀分布

btn_course = tk.Button(buttons_frame, text="课程列表", command=show_page_course)
btn_teacher = tk.Button(buttons_frame, text="教师列表", command=show_page_teacher)
btn_student = tk.Button(buttons_frame, text="学生列表", command=show_page_student)
btn_add_course = tk.Button(buttons_frame, text="添加课程",command=lambda:add_course.add_course_form(root,cursor,connection,on_success=refresh_course_page))
btn_add_teacher = tk.Button(buttons_frame, text="添加教师",command=lambda:add_teacher.add_teacher_form(root,cursor,connection,on_success=refresh_teacher_page))
btn_add_student = tk.Button(buttons_frame, text="添加学生",command=lambda:add_student.add_student_form(root,cursor,connection,on_success=refresh_student_page))

# 使用grid布局来排列按钮
btn_course.grid(row=0, column=0, padx=10, pady=10)
btn_teacher.grid(row=0, column=1, padx=10, pady=10)
btn_student.grid(row=0, column=2, padx=10, pady=10)
btn_add_course.grid(row=0, column=3, padx=10, pady=10)
btn_add_teacher.grid(row=0, column=4, padx=10, pady=10)
btn_add_student.grid(row=0, column=5, padx=10, pady=10)


# 运行主循环
root.mainloop()
