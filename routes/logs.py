from bottle import route


# CREATE log
@route('/logs', method="POST")
def create_log():
    pass


# READ (get) all logs
@route('/logs', method="GET")
def get_all_logs():
    # fetch all logs from database
    pass


# READ (get) log by id
@route('/logs/<id>', method="GET")
def get_log(id):
    pass


# UPDATE (patch in HTTP methods) log by id
@route('/logs/<id>', method='PATCH')
def update_log(id):
    pass


# DELETE log by id
@route('logs/<id>', method='DELETE')
def delete_log(id):
    pass
