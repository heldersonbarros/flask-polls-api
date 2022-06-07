from werkzeug.security import generate_password_hash, check_password_hash

class Account():
    def __init__(self, name, email, username, id=None, password=None):
        self.id = id
        self.name = name
        self.email = email
        self.username = username
        self.password = password
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)