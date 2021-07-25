import cx_Oracle
import logging
from api.common.connectSqlServer import ConnectSqlServer

logger = logging.getLogger('log')


class ConnectOracle(ConnectSqlServer):

    def __init__(self, username, password, ipport):
        self.username = username
        self.password = password
        self.params = ipport
        self.connect, self.cursor = self.conn()

    def conn(self):
        try:
            connect = cx_Oracle.connect(self.username, self.password, self.params)  # 服务器名,账户,密码,数据库名
            if connect:
                cursor = connect.cursor()  # 创建一个游标对象,python里的sql语句都要通过cursor来执行
                logger.info("链接ORACLE数据库成功!")
                return connect, cursor
        except Exception as e:
            logger.warning("Oracle连接失败，详细错误：" + str(e))
            return str(e), None

    def getAllDatabases(self):
        """获取数据库列表,"""
        self.cursor.execute("SELECT username FROM all_users order by username")
        res = [row[0] for row in self.cursor.fetchall()]
        return res

    def getAllTables(self):
        """获取table列表"""
        sql = """
            SELECT
	            table_name 
            FROM
	            user_tables 
            WHERE
	            nvl( tablespace_name, 'no tablespace' ) NOT IN ( 'SYSTEM', 'SYSAUX' ) 
	        AND IOT_NAME IS NULL
        """
        self.cursor.execute(sql)
        res = [row[0] for row in self.cursor.fetchall()]
        return res

    def getAllColumns(self, tableName, dbName):
        """
            获取table-columns列表
            COLUMN_NAME:COLUMN_NAME
            COLUMN_TYPE:字段类型。比如float(9,3)，varchar(50)。
            IS_NULLABLE:字段是否可以是NULL,该列记录的值是YES或者NO。
            CHARACTER_SET_NAME:字段字符集名称。比如utf8。
            COLUMN_KEY:索引类型。可包含的值有PRI，代表主键，UNI，代表唯一键，MUL，可重复。
            EXTRA:其他信息。比如主键的auto_increment。
            COLUMN_COMMENT:字段注释
        """
        sql = f"""
                SELECT
                    t.COLUMN_NAME AS columnName,
                    t.DATA_TYPE AS dataType,
                    t.character_set_name As character_set_name,
                    t.NULLABLE AS nullable,
                    c.COMMENTS AS columnComment
                FROM
                    user_tab_columns t,
                    user_col_comments c 
                WHERE
                    t.TABLE_NAME = c.TABLE_NAME 
                    AND t.COLUMN_NAME = c.COLUMN_NAME 
                    AND t.TABLE_NAME = '{tableName}'
                ORDER BY
                    t.COLUMN_ID
                """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        col = [i[0] for i in self.cursor.description]
        return col, result

    def describeTable(self, tableName):
        """建表语句"""
        sql = "select dbms_metadata.get_ddl('TABLE', '{0}') from dual".format(tableName)
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return result

    def getTableDatas(self, tableName):
        """获取table列表"""
        sql = 'select * from "{0}"'.format(tableName)
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        col = [i[0] for i in self.cursor.description]
        return col, result


if __name__ == '__main__':
    oracle19c = ConnectOracle("C##ZZHTEST", "zzhtest", "192.168.202.76:1521/ora12c")
    print(oracle19c.getTableDatas('!@#$%^&*()special特殊'))

    # oracle12c = ConnectOracle("c##zzhtest","zzhtest","192.168.202.76:1521/ora12c")
    # oracle12c_sql = 'select count(*) from "NOPK_NORMAL"'

    # oracle11g = ConnectOracle("test11g","test","192.168.202.43:1521/ora")
    # oracle11g_sql = 'select count(*) from "NOPK_NORMAL"'
    # print(oracle11g.validation_sql(oracle11g_sql))
