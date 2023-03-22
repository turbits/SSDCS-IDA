from bottle import template, get


@get('/')
def render_index():
    return template('templates/index.tpl')


@get('/login')
def render_login():
    return template('templates/login/index.tpl')


@get('/dashboard')
def render_dashboard():
    return template('templates/dashboard/index.tpl')
