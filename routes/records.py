from bottle import route


# CREATE record
@route('/records', method="POST")
def create_record():
    pass


# READ (get) all records
@route('/records', method="GET")
def get_all_records():
    # fetch all records from database
    pass


# READ (get) record by id
@route('/records/<id>', method="GET")
def get_record(id):
    pass


# UPDATE (patch in HTTP methods) record by id
@route('/records/<id>', method='PATCH')
def update_record(id):
    pass


# DELETE record by id
@route('records/<id>', method='DELETE')
def delete_record(id):
    pass
