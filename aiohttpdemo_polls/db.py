'''数据库相关'''
import aiopg.sa
# aiopg 是一个用于从 asyncio 框架访问数据库的库。 它包装Psycopg数据库驱动程序的异步特性
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date
)

__all__ = ['question', 'choice']
# meta是一个容器对象，它将描述的数据库（或多个数据库）的许多不同功能放在一起。
meta = MetaData()
# 数据库表和对象的映射
# Table(表名，元数据，列）
# 通过Table把表和Meta建立联系
question = Table(
    'question', meta,

    Column('id', Integer, primary_key=True),
    Column('question_text', String(200), nullable=False),
    Column('pub_date', Date, nullable=False)
)

choice = Table(
    'choice', meta,

    Column('id', Integer, primary_key=True),
    Column('choice_text', String(200), nullable=False),
    Column('votes', Integer, server_default="0", nullable=False),

    Column('question_id',
           Integer,
           ForeignKey('question.id', ondelete='CASCADE'))
)


class RecordNotFound(Exception):
    """Requested record in database was not found"""

# 初始化数据库
async def init_pg(app):
    conf = app['config']['postgres']
    # 建立一个连接池
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    # db是我们存放连接池的地方
    app['db'] = engine

# 关闭数据库
async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


# 获取问题
# 访问数据库列的方法
# tableName.colums.columName 简化为 tableName.c.cname
# conn是engine的connection 连接池的连接 用conn.execute来执行sql代码
async def get_question(conn, question_id):
    result = await conn.execute(
        question.select()
        .where(question.c.id == question_id))
    # first（）选取第一行记录
    question_record = await result.first()
    # 没有记录
    if not question_record:
        msg = "Question with id: {} does not exists"
        raise RecordNotFound(msg.format(question_id))
    # 有记录
    result = await conn.execute(
        choice.select()  # 在chice表中执行select命令
        .where(choice.c.question_id == question_id)
        .order_by(choice.c.id))
    choice_records = await result.fetchall() # fetchall 获取所有记录
    # assert record == list 是fetchone的list
    return question_record, choice_records

# 投票
async def vote(conn, question_id, choice_id):
    result = await conn.execute(
        choice.update() # 更新choice表
        .returning(*choice.c)
        .where(choice.c.question_id == question_id)
        .where(choice.c.id == choice_id)
        .values(votes=choice.c.votes+1))
    # 一条记录，类型像元组，可以直接下表访问，record[0],record[1]
    # 也可以当成字典访问，record['id']
    record = await result.fetchone()
    # isinstance(record, sqlalchemy.engine.result.RowProxy)
    if not record:
        msg = "Question with id: {} or choice id: {} does not exists"
        raise RecordNotFound(msg.format(question_id, choice_id))
