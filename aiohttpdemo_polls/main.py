#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Mr Wang'

import logging
import sys

import aiohttp_jinja2
import jinja2
from aiohttp import web

from aiohttpdemo_polls.db import close_pg, init_pg
from aiohttpdemo_polls.middlewares import setup_middlewares
from aiohttpdemo_polls.routes import setup_routes
from aiohttpdemo_polls.settings import get_config


# 初始化应用
# 这里是主要框架
async def init_app(argv=None):
    # 申请一个web应用，我们的网页的相关信息将要和它绑定
    app = web.Application()
    # 获取有关设置
    app['config'] = get_config(argv)
    # 设置渲染，也就是html相关的文件所在地
    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('aiohttpdemo_polls', 'templates'))

    # startup 建立数据库连接, 退出后则关闭
    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)

    # 设置视图和路由
    setup_routes(app)
    # 设置中间件
    setup_middlewares(app)

    return app


def main(argv):
    logging.basicConfig(level=logging.DEBUG) # 显示debug以上的日志

    app = init_app(argv)

    config = get_config(argv)
    web.run_app(app,
                host=config['host'],
                port=config['port'])


if __name__ == '__main__':
    main(sys.argv[1:])
