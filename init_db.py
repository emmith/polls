
'''初始化数据库'''
from sqlalchemy import create_engine, MetaData

from aiohttpdemo_polls.db import question, choice
from aiohttpdemo_polls.settings import BASE_DIR, get_config

# 建立连接的参数，可以学习这种写法
DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

ADMIN_DB_URL = DSN.format(
    user='postgres', password='password', database='postgres',
    host='localhost', port=5432
)
# 管理员的连接
admin_engine = create_engine(ADMIN_DB_URL, isolation_level='AUTOCOMMIT')

USER_CONFIG_PATH = BASE_DIR / 'config' / 'polls.yaml'
USER_CONFIG = get_config(['-c', USER_CONFIG_PATH.as_posix()])
USER_DB_URL = DSN.format(**USER_CONFIG['postgres'])
user_engine = create_engine(USER_DB_URL)

# 测试用的
TEST_CONFIG_PATH = BASE_DIR / 'config' / 'polls_test.yaml'
TEST_CONFIG = get_config(['-c', TEST_CONFIG_PATH.as_posix()])
TEST_DB_URL = DSN.format(**TEST_CONFIG['postgres'])
test_engine = create_engine(TEST_DB_URL)

# 包括建库，添加用户，设置密码，以及授权
def setup_db(config):

    db_name = config['database']
    db_user = config['user']
    db_pass = config['password']

    conn = admin_engine.connect()
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
    conn.execute("CREATE DATABASE %s ENCODING 'UTF8'" % db_name)
    conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                 (db_name, db_user))
    conn.close()

# 清除数据库
def teardown_db(config):

    db_name = config['database']
    db_user = config['user']

    conn = admin_engine.connect()
    conn.execute("""
      SELECT pg_terminate_backend(pg_stat_activity.pid)
      FROM pg_stat_activity
      WHERE pg_stat_activity.datname = '%s'
        AND pid <> pg_backend_pid();""" % db_name)
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.close()

# 建表 meta.create_all
def create_tables(engine=test_engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[question, choice])

# 卸表 meta.drop_all
def drop_tables(engine=test_engine):
    meta = MetaData()
    meta.drop_all(bind=engine, tables=[question, choice])

# 测试数据库
def sample_data(engine=test_engine):
    conn = engine.connect()
    conn.execute(question.insert(), [
        {'question_text': 'What\'s new?',
         'pub_date': '2015-12-15 17:17:49.629+02'}
    ])
    conn.execute(choice.insert(), [
        {'choice_text': 'Not much', 'votes': 0, 'question_id': 1},
        {'choice_text': 'The sky', 'votes': 0, 'question_id': 1},
        {'choice_text': 'Just hacking again', 'votes': 0, 'question_id': 1},
    ])
    conn.close()


if __name__ == '__main__':
    setup_db(USER_CONFIG['postgres'])
    create_tables(engine=admin_engine)
    sample_data(engine=admin_engine)
    # setup_db(TEST_CONFIG['postgres'])
    # create_tables(engine=test_engine)
    # sample_data(engine=test_engine)
    # # drop_tables()
    # #teardown_db(TEST_CONFIG['postgres'])
