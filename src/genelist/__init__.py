import binascii
import datetime
import os

from flask import Flask, redirect, request, render_template, session
import config

app = Flask(__name__)
conf = config.load_config()
app.secret_key = conf['SECRET_KEY'] if 'SECRET_KEY' in conf else binascii.hexlify(os.urandom(64))

start_time = datetime.datetime.now()


def uptime():
    td = datetime.datetime.now() - start_time
    s = ''
    if td.days > 0:
        s = '%sd'

    secs = td.seconds
    hours = secs / (60 * 60)
    if hours > 0:
        s += '%sh' % hours
        secs = secs - (hours * 60 * 60)

    mins = secs / 60
    if mins > 0:
        s += '%sm' % mins
        secs = secs - (mins * 60)

    s += '%ss' % secs
    return s


@app.route("/signout")
def signout():
    session.pop('uid', None)
    session.pop('username', None)
    return redirect("/")


@app.route("/auth",  methods=['GET', 'POST'])
def signin():
    if request.method == "GET":
        return render_template("auth.html")

    userid = auth.authenticate(request.form['username'], request.form['password'])
    if userid:
        session['uid'] = userid
        session['username'] = request.form['username']

        return redirect('/')
    else:
        error = 'Invalid username/password'
        return render_template("auth.html", error=error)


@app.route("/")
def main():
    return render_template("index.html", uptime=uptime())


@app.route("/foo")
def foo():
    res = ''
    conf.test()
    try:
        with conf.conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM test;")
            res = cur.fetchone()
            cur.close()
    except:
        return "Error testing connection"

    return "Hello foo.4..\n<hr/>" + str(res) + "<hr/>" + "<a href='/auth'>Sign in </a>"


@app.route("/resetdb")
def bar():
    conf.resetdb()
    return redirect('/foo')


def run(*args, **kwargs):
    app.run(*args, **kwargs)


import auth
