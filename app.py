import os
import sys
import click

from flask import (
    request,
    Flask,
    render_template,
    url_for,
    redirect,
    flash,
)

from flask_sqlalchemy import SQLAlchemy # 导入扩展类


WIN = sys.platform.startswith('win')
if WIN: # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else: # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控

app.config['SECRET_KEY'] = 'dev' # 等同于 app.secret_key = 'dev'
# 在扩展类实例化前，加载配置

db = SQLAlchemy(app) # 初始化扩展，传入程序实例 app


class User(db.Model): # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True) # 主键
    name = db.Column(db.String(20)) # 名字


class Todo(db.Model): # 表名将会是 todo
    id = db.Column(db.Integer, primary_key=True) # 主键
    title = db.Column(db.String(60)) # 标题
    type = db.Column(db.String(15))  # 类型



@app.cli.command() # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')
# 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop: # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.') # 输出提示信息


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()
    # 全局的两个变量移动到这个函数内
    name = "xsj"

    todos = [
    {"title": "The Litter Scheme","type": "PL",},
    {"title": "OSTEP","type": "OS",},
    {"title": "计算机程序的构造和解释","type": "PL",},
    {"title": "算法设计与分析","type": "Algorithm",},
    ]

    user = User(name=name)
    db.session.add(user)

    for m in todos:
        todo = Todo(title=m['title'], type=m['type'])
        db.session.add(todo)

    db.session.commit()
    click.echo('Done.')


@app.context_processor
def inject_user():
    user = User.query.first()

    return dict(user=user)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': # 判断是否是 POST 请求
        # 获取表单数据
        title = request.form.get('title') # 传入表单对应输入字段的 name 值
        type = request.form.get('type')

        # 验证数据
        if not title or not type or len(type) > 15 or len(title) > 60:
            flash('Invalid input.') # 显示错误提示
            return redirect(url_for('index')) # 重定向回主页

        # 保存表单数据到数据库
        todo = Todo(title=title, type=type) # 创建记录
        db.session.add(todo) # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('Item created.') # 显示成功创建的提示

        return redirect(url_for('index')) # 重定向回主页

    todos = Todo.query.all()

    return render_template("index.html", todos=todos)


@app.route('/todo/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if request.method == 'POST': # 处理编辑表单的提交请求
        title = request.form['title']
        type = request.form['type']

        if not title or not type or len(type) > 15 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=todo_id))# 重定向回对应的编辑页面

        todo.title = title # 更新标题
        todo.type = type   # 更新类型
        db.session.commit() # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index')) # 重定向回主页

    return render_template('edit.html', todo=todo)


@app.route('/todo/delete/<int:todo_id>', methods=['POST']) # 限定只接受 POST 请求
def delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo) # 删除对应的记录
    db.session.commit()     # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    user = User.query.first()
    print(user)

    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        debug=True,
        port=81,
    )



