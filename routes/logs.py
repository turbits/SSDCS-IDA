from bottle import get, post, delete, route


# CREATE log
@post('/logs')
def create_log():
    pass


# READ (get) all logs
@get('/logs')
def get_all_logs():
    # fetch all logs from database
    pass


# READ (get) log by id
@get('/logs/<id>')
def get_log(id):
    pass


# UPDATE (patch in HTTP methods) log by id
@route('/logs/<id>', method='PATCH')
def update_log(id):
    pass


# DELETE log by id
@delete('logs/<id>')
def delete_log(id):
    pass
