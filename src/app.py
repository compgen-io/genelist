#!/usr/bin/env python

import os

import config

from flask import Flask, redirect

app = Flask(__name__)
conf = config.load_config()


@app.route("/")
def main():
    return "Hello there..."


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

    return "Hello foo.1..\n<hr/>" + str(res)


@app.route("/resetdb")
def bar():
    conf.resetdb()
    return redirect('/foo')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=os.environ['APP_ENV'] == 'dev' if 'APP_ENV' in os.environ else False)
