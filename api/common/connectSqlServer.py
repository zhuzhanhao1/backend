import logging
import traceback
import pymssql
import sqlparse

logger = logging.getLogger('log')


class ConnectSqlServer:

    def __init__(self, username, password, host, db_name, port=1433, timeout=300, login_timeout=10):
        self.username = username
        self.password = password
        self.host = host
        self.db_name = db_name
        self.timeout = timeout
        self.login_timeout = login_timeout
        self.port = port
        self.connect, self.cursor = self.conn()

    def conn(self):
        try:
            connect = pymssql.connect(server=self.host, user=self.username, password=self.password,
                                      database=self.db_name, timeout=self.timeout, port=self.port,
                                      charset='utf8')  # 服务器名,账户,密码,数据库名
            if connect:
                cursor = connect.cursor()  # 创建一个游标对象,python里的sql语句都要通过cursor来执行
                logger.info("连接SqlServer数据库成功!")
                return connect, cursor
        except Exception as e:
            logger.warning("Sql Server连接失败，详细错误：" + str(e))
            return str(e), None

    def executeSql(self, sql):
        """原生执行语句"""
        # if not self.connect:
        #     return "连接数据库异常，请检查数据库服务是否启动"
        # logger.info("")
        try:
            # for statement in sqlparse.split(sql):  # 分割SQL语句
            #     print(statement)
            #     self.cursor.execute(statement)
            logger.info("运行SQL：" + sql)
            self.cursor.execute(sql)
            self.connect.commit()
            logger.info("SQL执行成功")
            return "成功"
        except Exception as e:
            # logger.warning(f"sql执行用例运行失败，错误信息{traceback.format_exc()}")
            logger.warning("sql执行用例运行失败，失败原因：" + str(e))
            return str(e)

    def validationSql(self, sql):
        """fetchone返回的是tuple,fetchall返回的是list"""
        try:
            if "COUNT" not in sql and "count" not in sql:
                logger.warning("验证语句中必须包含count")
                return (-2,)
            logger.info("查询数量SQL：" + sql)
            for statement in sqlparse.split(sql):  # 分割SQL语句
                self.cursor.execute(statement)
            resTuple = self.cursor.fetchone()
            logger.info("COUNT数量查询结果为：<" + str(resTuple[0]) + ">")
            return resTuple
        except Exception as e:
            logger.warning("COUNT数量查询用例运行失败：" + str(e))
            return (-1,)

    def closeConn(self):
        if self.cursor:
            self.cursor.close()
        if self.connect:
            self.connect.close()
        return

    def getAllDatabases(self):
        """获取数据库列表,"""
        sql = """SELECT Name FROM Master..SysDatabases ORDER BY Name"""
        self.cursor.execute(sql)
        res = [row[0] for row in self.cursor.fetchall()]
        return res

    def getAllTables(self):
        """获取table列表"""
        sql = """SELECT * from sysobjects where xtype = 'u' and name not like '%_CT' ORDER BY Name"""
        self.cursor.execute(sql)
        res = [row[0] for row in self.cursor.fetchall()]
        print(res)
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
--                 表名 = case when a.colorder=1 then d.name else '' end,
--                 表说明 = case when a.colorder=1 then isnull(f.value,'') else '' end,
--                 字段序号 = a.colorder,
                字段名 = a.name,
                标识 = case when COLUMNPROPERTY( a.id,a.name,'IsIdentity')=1 then '√'else '' end,
                主键 = case when exists(SELECT 1 FROM sysobjects where xtype='PK' and parent_obj=a.id and name in (
                SELECT name FROM sysindexes WHERE indid in( SELECT indid FROM sysindexkeys WHERE id = a.id AND colid=a.colid))) then '√' else '' end,
                类型 = b.name,
                占用字节数 = a.length,
                长度 = COLUMNPROPERTY(a.id,a.name,'PRECISION'),
                小数位数 = isnull(COLUMNPROPERTY(a.id,a.name,'Scale'),0),
                允许空 = case when a.isnullable=1 then '√'else '' end,
                默认值 = isnull(e.text,''),
                字段说明 = isnull(g.[value],'')
                FROM
                syscolumns a
                left join
                systypes b
                on
                a.xusertype=b.xusertype
                inner join
                sysobjects d
                on
                a.id=d.id and d.xtype='U' and d.name<>'dtproperties'
                left join
                syscomments e
                on
                a.cdefault=e.id
                left join
                sys.extended_properties g
                on
                a.id=G.major_id and a.colid=g.minor_id
                left join
                sys.extended_properties f
                on
                d.id=f.major_id and f.minor_id=0
                where d.name='{tableName}'
                order by
                a.id,a.colorder
                """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        col = [i[0] for i in self.cursor.description]
        return col, result

    def describeTable(self, tableName):
        """return ResultSet 类似查询"""
        sql = ""
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return result[1]

    def getTableDatas(self, tableName):
        """获取table列表"""
        sql = f"""select * from "{tableName}";"""
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        col = [i[0] for i in self.cursor.description]
        return col, result


if __name__ == '__main__':
    a = ConnectSqlServer('sa', 'Hzmc321#', '192.168.238.121', 'zzhtest', 1433)
    a.getTableDatas('中文表')
