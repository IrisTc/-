import mysql.connector
'''这个模块包含mysql连接器功能'''

class ConnectionError(Exception):
    pass

class CredentialsError(Exception):
    pass

class SQLError(Exception):
    pass

class SQLError(Exception):
    pass

class UseDatabase:

    '''初始化usedatabase的所有属性，接受一个参数，config为连接属性字典，保存到configuration属性'''
    def __init__(self, config: dict) -> None:
        self.configuration = config

    '''执行需要在with语句代码组运行前先执行的建立代码'''
    '''需要使用存储在self.configuration中的配置属性来连接数据库并创建游标，返回游标'''
    def __enter__(self) -> 'cursor':
        try:
            self.conn = mysql.connector.connect(**self.configuration)
            self.cursor = self.conn.cursor()
            return self.cursor
        except mysql.connector.errors.InterfaceError as err:
            raise ConnectionError(err)
        except mysql.connector.errors.ProgrammingError as err:
            raise CredentialsError(err)

    '''执行在with语句结束时运行的清理代码'''
    '''向数据库提交数据，关闭游标和连接，处理with代码组中可能出现的任何异常'''
    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        if exc_type is mysql.connector.errors.ProgrammingError:
            raise SQLError(exc_value)
        elif exc_type:
            raise exc_type(exc_value)
