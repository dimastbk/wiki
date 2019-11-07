from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', index=True)


@app.route('/status')
def status():
    import subprocess
    import re

    pipe = subprocess.PIPE
    p = subprocess.Popen('qstat', shell=True, stdin=pipe, stdout=pipe,
                         stderr=subprocess.STDOUT, close_fds=True,
                         cwd='/data/project/dimastbkbot/')
    comp = re.compile(r'(?P<jobID>\d+) (?P<prior>.*?) (?P<name>.*?) ' /
                      r'(?P<user>.*?) (?P<state>\w+) \s+ (?P<submit>.*?) ' /
                      r'(?P<startat>.*?) (?P<queue>.*?) ')
    ret = comp.findall(p.stdout.read())
    return render_template('status.html', content=ret, status=True)


@app.route('/crontab')
def crontab():
    return render_template('crontab.html', crontab=True)
