import os
import sys
import json
import atexit

from functools import wraps
from flask import redirect, render_template, session, g, request, Blueprint, url_for

from genelist import app, conf, uptime

site = Blueprint('site', __name__, template_folder='templates', static_folder='static')

import support
print dir(site)


try:
    dblogger = support.dblogger.DBLogger(conf.build_db_conn())
    app.logger.addHandler(dblogger)

    def close_dblogger():
        dblogger.close()

    atexit.register(close_dblogger)

except:
    dblogger = None
    sys.stderr.write("Unable to setup DB Logger!\n")

import cbplims.users
import cbplims.projects


# Let's just load a DB connection before each request
@site.before_request
def before_request_wrapper():
    if request.path in [url_for('site.resetdb'), url_for('site.resetdb')]:
        return

    spl = request.path.split("/")
    if len(spl) > 2 and spl[2] == 'static':
        is_static = True
    else:
        is_static = False

    if not request.path in [url_for('site.view_dblogger'), url_for('site.dbconsole')]:
        if not is_static:
            app.logger.debug(request.method+" "+request.path)

    g.uptime = uptime.uptime_str()
    g.dbconn = conf.get_db_conn()
    g.debug = True if 'APP_ENV' in os.environ and os.environ['APP_ENV'] == 'dev' else False

    g.is_project_admin = False
    g.is_project_view = False
    g.user = None
    g.project = None

    if 'uid' in session and session['uid']:
        g.user = cbplims.users.get_user(session['uid'])
        g.allow_switch_project = True
        if not g.user.is_global_admin:
            avail = cbplims.projects.get_available_projects(g.user.id)
            if len(avail) == 1:
                g.allow_switch_project = False

    if 'pid' in session and session['pid']:
        g.project = cbplims.projects.get_project(session['pid'])
        if g.project:
            auth_level = cbplims.projects.get_project_auth_level(g.user.id, g.project.id)
            if auth_level == 'admin':
                g.is_project_admin = True
            elif auth_level == 'view':
                g.is_project_view = True


# Be sure to close it
@site.teardown_request
def teardown_request_wrapper(err):
    if err:
        app.logger.error(err)
        print "Error: %s " % err

    try:
        if g.dbconn:
            conf.put_db_conn(g.dbconn)
    except Exception, e:
        app.logger.error(e)
        print e


def requires_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user:
            return redirect(url_for('site.signin'))

        return f(*args, **kwargs)
    return decorated


def requires_project(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user:
            return redirect(url_for('site.signin'))
        if not g.project:
            return redirect(url_for('site.switch_project'))

        return f(*args, **kwargs)
    return decorated


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user:
            return redirect(url_for('site.signin'))

        if not g.user.is_global_admin:
            if not g.project:
                return redirect(url_for('site.switch_project'))
            if not g.is_project_admin:
                return redirect(url_for('site.index'))

        return f(*args, **kwargs)
    return decorated


def requires_global_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user:
            return redirect(url_for('site.signin'))

        if not g.user.is_global_admin:
            return redirect(url_for('site.index'))

        return f(*args, **kwargs)
    return decorated


@site.route("/")
@requires_project
def index():
    return render_template("index.html")


@site.route("/settings/")
@requires_project
def settings():
    return render_template("settings/index.html")


@site.route("/test")
def foo():
    res = ''
    conf.test()
    try:
        cur = g.dbconn.cursor()
        cur.execute("SELECT * FROM users;")
        for record in cur:
            res += str(record)+"<br/>"

        cur.close()
    except Exception, e:
        return "Testing\n<hr/>" + str(e) + "<hr/>" + "Uptime=" + uptime.uptime_str()

    return "Testing\n<hr/>It works!<br/><br/>Users:<br/>" + str(res) + "<hr/>" + "Uptime=" + uptime.uptime_str()


@site.route("/resetdb")
def resetdb():
    app.logger.info("Reloading DB at user request")

    global dblogger
    if dblogger:
        dblogger.close()
        app.logger.removeHandler(dblogger)

        dblogger = support.dblogger.DBLogger(conf.build_db_conn())
        app.logger.addHandler(dblogger)

    conf.initdb()
    return redirect('/')


@site.route("/log")
@requires_admin
def view_dblogger():
    if not dblogger:
        return "Log not available"

    # app.logger.debug(str(request.args))

    def json_str(obj):
        print "Serializing: %s" % obj
        return str(obj)

    if 'last' in request.args:
        try:
            messages = dblogger.fetch_messages(int(request.args['last']))
            s = json.dumps([x._asdict() for x in messages], default=json_str)
            return s
        except Exception, e:
            print e
            return e
    else:
        messages = dblogger.fetch_messages()
        return render_template('dblogger.html', messages=messages)


@site.route("/dbconsole", methods=['GET', 'POST'])
@requires_global_admin
def dbconsole():
    if request.method == "GET":
        return render_template("dbconsole.html", records=[])

    elif request.method == "POST":
        query = request.form["query"].strip()
        records = []
        names = []
        msg = ""

        if query:
            app.logger.debug("SQL: %s", query)

            try:
                cur = g.dbconn.cursor()
                cur.execute(query)

                if cur.rowcount == 1:
                    msg = "1 record"
                else:
                    msg = "%s records" % cur.rowcount

                if query.upper()[:6] == "SELECT":
                    records = list(cur.fetchall())
                    names = [x[0] for x in cur.description]
                else:
                    g.dbconn.commit()

            except Exception, e:
                app.logger.error(e)
                msg = str(e)

            cur.close()

        return render_template('dbconsole.html', records=records, names=names, query=query, msg=msg)


@site.route("/restart")
def restart_app():
    app.logger.info("Restarting app at user request")
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return render_template('restart.html')


import auth.view
import users.view
import projects.view

if False:
    print auth
    print projects
