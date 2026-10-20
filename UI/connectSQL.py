# 导入 pyodbc 库，用于连接和操作多种数据库，包括 SQL Server
import pyodbc

# 指定 SQL Server 实例的名称或 IP 地址
server = 'LAPTOP-BN49AST2'
# 指定要连接的数据库名称
database = 'OLPMS'
# 指定连接数据库的用户名
username = 'sa'
# 指定连接数据库的密码
password = '12345678'#这里要输入数据库的密码！！！！

# 构建连接字符串，包含了连接到数据库所需的所有信息
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# 使用 pyodbc 库的 connect 函数连接到 SQL Server 数据库
connection = pyodbc.connect(connection_string)

# 创建一个游标对象，用于执行 SQL 查询和操作数据库
cursor = connection.cursor()


