import os

from flask import render_template, send_from_directory

from apps import app


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/status')
def status():
    import subprocess
    import re

    pipe = subprocess.PIPE
    p = subprocess.Popen('qstat', shell=True, stdin=pipe, stdout=pipe,
                         stderr=subprocess.STDOUT, close_fds=True,
                         cwd='/data/project/dimastbkbot/')
    comp = re.compile(r'(?P<jobID>\d+) (?P<prior>.*?) (?P<name>.*?) '
                      r'(?P<user>.*?) (?P<state>\w+) \s+ (?P<submit>.*?) '
                      r'(?P<startat>.*?) (?P<queue>.*?) ')
    ret = comp.findall(p.stdout.read())
    return render_template('status.html', content=ret)


@app.route('/crontab')
def crontab():
    return render_template('crontab.html')


@app.route('/src')
def src():
    filelist = {}
    i = 0
    for filename in sorted(os.listdir(os.path.join(app.config['SRC_PATH']))):
        if filename[-3:] == '.py':
            filelist[i] = filename
            i += 1

    return render_template('source.html', filelist=filelist)


@app.route('/src/<path:filename>')
def send_src(filename):
    return send_from_directory(app.config['SRC_PATH'], filename)
