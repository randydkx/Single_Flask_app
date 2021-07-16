from operator import truediv
from flask import Flask, render_template, request, session
from flask.helpers import flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.form import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


import pymysql
pymysql.install_as_MySQLdb()


app = Flask(__name__)

'''
1.配置数据库
2.添加书和作者模型
3.添加数据
4.使用模板显示数据库中查询的数据
5.使用WTF渲染数据
6.实现增删改查
'''
# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:17851093886@127.0.0.1/flask_books'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'luowenshui'

db = SQLAlchemy(app)

# 定义书和作者模型


class Author(db.Model):
    __tablenam__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    # books为自己使用的变量，其中author是为book使用的变量
    books = db.relationship('Book', backref='author')

    def __repr__(self):
        return 'Author: {author}'.format(self.name)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    def __repr__(self):
        return 'Book: %s  %s' % (self.name, self.author_id)

# 自定义表单类


class AuthorForm(FlaskForm):
    author = StringField('作者', validators=[DataRequired()])
    book = StringField('书籍', validators=[DataRequired()])
    submit = SubmitField('提交')


@app.route('/', methods=['GET', 'POST'])
def index():
    author_form = AuthorForm()
    if author_form.validate_on_submit():
        author_name = author_form.author.data
        book_name = author_form.book.data
        author = Author.query.filter_by(name=author_name).first()
        if author:
            book = Book.query.filter_by(name=book_name).first()
            if book:
                flash('已存在同名书籍')
            else:
                try:
                    new_book = Book(name=book_name, author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    flash('添加书籍失败')
                    db.session.rollback()
        else:
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()
                new_book = Book(name=book_name, author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print(e)
                flash('添加失败')
                db.session.rollback()
    else:
        if request.method == 'POST':
            flash('参数不全')
    authors = Author.query.all()
    return render_template('books.html', author_form=author_form, authors=authors)


# 删除数据
@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    # 通过id获取直接通过query.get即可
    book = Book.query.get(book_id)
    
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除错误')
            db.session.rollback()
    else:
        flash('书籍找不到')
    # 执行完删除之后就返回当前网址
    # 重定向并传入视图函数，返回视图函数对应的路由地址
    return redirect(url_for('index'))
    # return redirect(url_for('/'))


@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    author = Author.query.get(author_id)
    if author:
        try: 
            # 先把作者的书删除，然后再将作者删除
            # 查询之后直接删除
            Book.query.filter_by(author_id=author_id).delete()
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除作者错误，无法查找到对应的作者')
            db.session.rollback()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 删除数据库中的相关表
    db.drop_all()
    # 创建数据库中的表
    db.create_all()
    # 向数据库中插入数据
    au1 = Author(name='老王')
    au2 = Author(name='老慧')
    au3 = Author(name='老刘')

    db.session.add_all([au1, au2, au3])
    db.session.commit()
    bk1 = Book(name='老王回忆录', author_id=au1.id)
    bk2 = Book(name='fasdfadsfds', author_id=au1.id)
    bk3 = Book(name='123123213', author_id=au2.id)
    bk4 = Book(name='jghj', author_id=au3.id)
    bk5 = Book(name='fadfaew', author_id=au3.id)

    db.session.add_all([bk1, bk2, bk3, bk4, bk5])

    db.session.commit()

    app.run(debug=True)
