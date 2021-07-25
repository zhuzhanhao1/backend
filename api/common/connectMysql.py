import logging
import traceback
import pymysql
from api.common.connectSqlServer import ConnectSqlServer

logger = logging.getLogger('log')


class ConnectMysql(ConnectSqlServer):

    def __init__(self, host, username, password, db_name, prot=3306, read_timeout=None):
        # super().__init__(username, password, host, db_name)
        self.username = username
        self.password = password
        self.host = host
        self.db_name = db_name
        self.port = int(prot)
        self.read_timeout = read_timeout
        self.connect, self.cursor = self.conn()

    def conn(self):
        try:
            connect = pymysql.connect(host=self.host, port=self.port, user=self.username, password=self.password,
                                      database=self.db_name, charset='utf8'
                                      )  # 服务器名,账户,密码,数据库名,read_timeout=self.read_timeout
            if connect:
                cursor = connect.cursor()  # 创建一个游标对象,python里的sql语句都要通过cursor来执行
                logger.info("连接MySQL数据库成功!")
                return connect, cursor
        except Exception as e:
            logger.error("Mysql连接失败，详细错误：" + str(e))
            # logger.error(traceback.format_exc())
            return str(e), None

    def getAllDatabases(self):
        """获取数据库列表,"""
        sql = "show databases"
        self.cursor.execute(sql)
        res = [row[0] for row in self.cursor.fetchall()]
        return res

    def getAllTables(self):
        """获取table列表"""
        self.cursor.execute("show tables")
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
        sql = f"""SELECT 
            COLUMN_NAME,
            COLUMN_TYPE,
            CHARACTER_SET_NAME,
            IS_NULLABLE,
            COLUMN_KEY,
            EXTRA,
            COLUMN_COMMENT
        FROM
            information_schema.COLUMNS
        WHERE
            TABLE_NAME = '{tableName}'
            AND TABLE_SCHEMA = '{dbName}'
        ORDER BY ORDINAL_POSITION;"""
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        col = [i[0] for i in self.cursor.description]
        return col, result

    def describeTable(self, tableName):
        """建表语句"""
        sql = f"show create table `{tableName}`;"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return result[1]

    def getTableDatas(self, tableName):
        """获取table列表"""
        sql = f"select * from `{tableName}`;"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        col = [i[0] for i in self.cursor.description]
        # data = list(map(list, result))
        # data = pd.DataFrame(data, columns=col)
        return col, result


if __name__ == '__main__':
    mysql8 = ConnectMysql('192.168.202.1', 'root', 'mypassword', 'zzhtest', 3306)
    mysql8.getAllColumns("NOPK_NORMAL")
