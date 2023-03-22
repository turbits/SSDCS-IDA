from bottle import get, post, delete, route


# CREATE user
@post('/users')
def create_user():
    pass


# READ (get) all users
@get('/users')
def get_all_users():
    # fetch all users from database
    pass


# READ (get) user by id
@get('/users/<id>')
def get_user(id):
    pass


# UPDATE (patch in HTTP methods) user by id
@route('/users/<id>', method='PATCH')
def update_user(id):
    pass


# DELETE user by id
@delete('users/<id>')
def delete_user(id):
    pass
