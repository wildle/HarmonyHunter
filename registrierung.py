from tinydb import TinyDB, Query

class Registrierung:
    db = TinyDB('login.json')  # Annahme: 'login.json' ist der Name der TinyDB-Datenbankdatei
    
    def __init__(self, username, email, password):
        """
        Initialisiert eine Instanz der Registrierungsklasse mit Benutzername, E-Mail und Passwort.

        :param username: Benutzername
        :param email: E-Mail-Adresse
        :param password: Passwort
        """
        self.username = username
        self.email = email
        self.password = password
    
    def store(self):
        """
        Speichert die Benutzerdaten in der Datenbank.
        """
        self.db.insert({'username': self.username, 'email': self.email, 'password': self.password})
    
    @classmethod
    def get_db_connector(cls):
        """
        Gibt den Datenbankconnector zurück.

        :return: TinyDB-Datenbankconnector
        """
        return cls.db

    @classmethod
    def find_by_username(cls, username):
        """
        Sucht nach einem Benutzer anhand des Benutzernamens.

        :param username: Benutzername
        :return: Liste der gefundenen Benutzerdatensätze
        """
        User = Query()
        return cls.db.search(User.username == username)

    @classmethod
    def find_by_email(cls, email):
        """
        Sucht nach einem Benutzer anhand der E-Mail-Adresse.

        :param email: E-Mail-Adresse
        :return: Liste der gefundenen Benutzerdatensätze
        """
        User = Query()
        return cls.db.search(User.email == email)

    @classmethod
    def find_by_username_and_password(cls, username, password):
        """
        Sucht nach einem Benutzer anhand von Benutzername und Passwort.

        :param username: Benutzername
        :param password: Passwort
        :return: Liste der gefundenen Benutzerdatensätze
        """
        User = Query()
        return cls.db.search((User.username == username) & (User.password == password))
