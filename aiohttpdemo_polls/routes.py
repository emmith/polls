# routes.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Mr Wang'


import pathlib

from .views import index, poll, results, vote


PROJECT_ROOT = pathlib.Path(__file__).parent

# 路由指定跳转的页面
def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/poll/{question_id}', poll, name='poll')
    app.router.add_get('/poll/{question_id}/results',
                       results, name='results')
    app.router.add_post('/poll/{question_id}/vote', vote, name='vote')
    setup_static_routes(app)


def setup_static_routes(app):
    app.router.add_static('/static/',
                          path=PROJECT_ROOT / 'static',
                          name='static')
