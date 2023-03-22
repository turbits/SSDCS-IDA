from bottle import get, post, delete, route


# CREATE record
@post('/records')
def create_record():
    pass


# READ (get) all records
@get('/records')
def get_all_records():
    # fetch all records from database
    pass


# READ (get) record by id
@get('/records/<id>')
def get_record(id):
    pass


# UPDATE (patch in HTTP methods) record by id
@route('/records/<id>', method='PATCH')
def update_record(id):
    pass


# DELETE record by id
@delete('records/<id>')
def delete_record(id):
    pass
