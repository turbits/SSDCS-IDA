from bottle import template, get, post, request, response
from utility.validate_data import validate_username, validate_password


# GETs
@get('/')
def render_index():
    return template('templates/index.tpl')


@get('/login')
def render_login():
    return template('templates/login/index.tpl')


@get('/dashboard')
def render_dashboard():
    return template('templates/dashboard/index.tpl')


# POSTs
@post('/login')
def login():
    # get the username and password from the form
    username = request.forms.get('username')
    password = request.forms.get('password')
    
    # validate username and pw
    _username_check = validate_username(username)
    _password_check = validate_password(password)
    
    # if either of the checks fail, return an error
    if _username_check is not True or _password_check is not True:
        return template('templates/login/index.tpl', error='Invalid username or password.')
    
    cookie_val = str('the UUID of the user')
    # if we were to harden this, we could add the 'domain' parameter, among others: https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/ (Nadalin, 2018)
    response.set_cookie('user_uuid', cookie_val, path='/', max_age=3600)
    
    return template('templates/dashboard/index.tpl')

# Nadalin, A. (2018) Web Security: How to Harden your HTTP cookies. Available at: [https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/](https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/) [Accessed 28 March 2023]
