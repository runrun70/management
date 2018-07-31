#from datetime import datetime
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from management.auth import login_required
from management.db import get_db
from werkzeug.utils import secure_filename
import os, zipfile, datetime

bp = Blueprint('book', __name__, url_prefix='/file')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','zip','c','cpp','py'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
@login_required
def index_book():
    """書籍の一覧を取得する"""

    # DBと接続
    db = get_db()

    # 書籍データを取得
    user_id = session.get('user_id')
    books = db.execute('SELECT * FROM version WHERE user_id = ? ORDER BY id DESC', (user_id,)).fetchall()
    user_name = db.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()
    # 書籍一覧画面へ遷移
    return render_template('book/index_book.html',
                           books=books,
                           title='ログイン',
                           username = str(user_name['username']),
                           year=datetime.datetime.now().year)


@bp.route('/add_file', methods=('GET', 'POST'))
@login_required
def create_book():
    """
    GET ：書籍登録画面に遷移
    POST：書籍登録処理を実施
    """
    db = get_db()
    if request.method == 'GET':
        # 書籍登録画面に遷移
        return render_template('book/create_book.html',
                               title='ファイルの追加',
                               year=datetime.datetime.now().year)


    # 書籍登録処理

    # ユーザーIDを取得
    user_id = session.get('user_id')
    user_name = db.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()
    path = os.getcwd()
    UPLOAD_FOLDER = (path+'/data/'+str(user_name['username'])+'/')

    # 登録フォームから送られてきた値を取得
    version = request.form['version']
    date_raw = datetime.datetime.now()
    date = ('{:%Y-%m-%d-%H-%M}'.format(date_raw))
    print(date)
    comment = request.form['comment']

    #print(path+UPLOAD_DIR)
    # DBと接続
    db = get_db()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルがありません.')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('不正なファイルです．')
            return redirect(request.url)
        file_list = os.listdir(UPLOAD_FOLDER)
        print(file_list)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            books = db.execute('SELECT * FROM version WHERE user_id = ? ORDER BY id DESC', (user_id,)).fetchall()
            if name not in file_list: 
                os.mkdir(UPLOAD_FOLDER+name)
                
            file_list2 = os.listdir(UPLOAD_FOLDER+name+'/')
            print(file_list2)
            print(UPLOAD_FOLDER+name+'/'+version+ext)
            if os.path.isfile(UPLOAD_FOLDER+name+'/'+version+ext):
                flash('すでに存在するヴァージョンです．')
                return redirect(request.url)
            file.save(os.path.join(UPLOAD_FOLDER+name+'/', version+ext))
            dir = './data/'+name+'/'+version+ext
           
    db.execute('INSERT INTO version (user_id,version, file_name, comment, dir) VALUES (?, ?, ?, ?, ?)',
        (user_id, version, name, comment, dir,))
    db.commit()

    # 書籍一覧画面へ遷移
    flash('ファイルを追加しました．', category='alert alert-info')
    return redirect(url_for('book.index_book'))




def get_book_and_check(book_id):
    """書籍の取得と存在チェックのための関数"""

    # 書籍データの取得
    db = get_db()
    book = db.execute('SELECT * FROM book WHERE id = ? ', (book_id,)).fetchone()

    if book is None:
        abort(404, 'There is no such book!!')

    return book
