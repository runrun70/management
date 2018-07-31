"""
FlaskアプリケーションのRouteとView
"""

from datetime import datetime
from flask import render_template
from management import app

@app.route('/')
@app.route('/home')
def home():
    """インデックスページの表示"""
    return render_template(
        'index.html',
        title='管理',
        year=datetime.now().year,
    )
