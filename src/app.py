#!/usr/bin/env python

from flask import Flask
app = Flask(__name__)


@app.route("/")
def main():
    return "Hello there..."


@app.route("/foo")
def foo():
    return "Hello again..."


@app.route("/bar")
def bar():
    return "Hello again2..."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
