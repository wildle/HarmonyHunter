from tinydb import TinyDB, Query

class Registrierung:
    db = TinyDB('login.json')  # Assuming login.json is the name of your TinyDB database file
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
    
    def store(self):
        self.db.insert({'username': self.username, 'email': self.email, 'password': self.password})
    
    @classmethod
    def get_db_connector(cls):
        return cls.db

    @classmethod
    def find_by_username(cls, username):
        User = Query()
        return cls.db.search(User.username == username)

    @classmethod
    def find_by_email(cls, email):
        User = Query()
        return cls.db.search(User.email == email)

    @classmethod
    def find_by_username_and_password(cls, username, password):
        User = Query()
        return cls.db.search((User.username == username) & (User.password == password))
