import sqlite3

DB_NAME = 'cinema.db'


class Database:
    def __init__(self, db_name=DB_NAME):
        self.con = sqlite3.connect(db_name)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()
        # sqlite ignores foreign keys unless this is turned on
        self.cur.execute('PRAGMA foreign_keys = ON')
        self.create_tables()

    def create_tables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer'
                CHECK (role IN ('customer', 'admin')),
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')))''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT,
            synopsis TEXT,
            actors TEXT,
            poster TEXT,
            age_rating INTEGER,
            rating REAL CHECK (rating BETWEEN 0 AND 10),
            duration_minutes INTEGER,
            release_date TEXT)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS cinemas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT,
            address TEXT)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS halls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cinema_id INTEGER NOT NULL
                REFERENCES cinemas(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            hall_type TEXT NOT NULL DEFAULT 'standard',
            total_seats INTEGER NOT NULL CHECK (total_seats > 0))''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS showtimes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL
                REFERENCES movies(id) ON DELETE CASCADE,
            hall_id INTEGER NOT NULL
                REFERENCES halls(id) ON DELETE CASCADE,
            show_date TEXT NOT NULL,
            show_time TEXT NOT NULL,
            ticket_price INTEGER NOT NULL CHECK (ticket_price >= 0),
            UNIQUE (hall_id, show_date, show_time))''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS food (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            size TEXT,
            price INTEGER NOT NULL CHECK (price >= 0),
            quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0))''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            showtime_id INTEGER NOT NULL REFERENCES showtimes(id),
            total_price INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'confirmed'
                CHECK (status IN ('confirmed', 'cancelled')),
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')))''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL
                REFERENCES bookings(id) ON DELETE CASCADE,
            showtime_id INTEGER NOT NULL REFERENCES showtimes(id),
            seat_number INTEGER NOT NULL,
            price INTEGER NOT NULL,
            UNIQUE (showtime_id, seat_number))''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS booking_food (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL
                REFERENCES bookings(id) ON DELETE CASCADE,
            food_id INTEGER NOT NULL REFERENCES food(id),
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            price INTEGER NOT NULL)''')
        self.con.commit()

    def close(self):
        self.con.close()


class Table:
    table = ''
    columns = ()

    def __init__(self, db):
        self.db = db

    def _check_columns(self, data):
        for column in data:
            if column not in self.columns:
                raise ValueError(f'unknown column: {column}')

    def _fetch_all(self, sql, params=()):
        self.db.cur.execute(sql, params)
        return [dict(row) for row in self.db.cur.fetchall()]

    def _fetch_one(self, sql, params=()):
        self.db.cur.execute(sql, params)
        row = self.db.cur.fetchone()
        return dict(row) if row else None

    def add(self, **data):
        self._check_columns(data)
        names = ', '.join(data)
        marks = ', '.join('?' for _ in data)
        self.db.cur.execute(
            f'INSERT INTO {self.table} ({names}) VALUES ({marks})',
            tuple(data.values()))
        self.db.con.commit()
        return self.db.cur.lastrowid

    def get(self, row_id):
        return self._fetch_one(
            f'SELECT * FROM {self.table} WHERE id = ?', (row_id,))

    def get_all(self):
        return self._fetch_all(f'SELECT * FROM {self.table}')

    def find(self, **data):
        self._check_columns(data)
        where = ' AND '.join(f'{column} = ?' for column in data)
        return self._fetch_all(
            f'SELECT * FROM {self.table} WHERE {where}',
            tuple(data.values()))

    def update(self, row_id, **data):
        if not data:
            return False
        self._check_columns(data)
        changes = ', '.join(f'{column} = ?' for column in data)
        self.db.cur.execute(
            f'UPDATE {self.table} SET {changes} WHERE id = ?',
            tuple(data.values()) + (row_id,))
        self.db.con.commit()
        return self.db.cur.rowcount > 0

    def delete(self, row_id):
        # returns False when the row is missing or still used by a booking
        try:
            self.db.cur.execute(
                f'DELETE FROM {self.table} WHERE id = ?', (row_id,))
        except sqlite3.IntegrityError:
            self.db.con.rollback()
            return False
        self.db.con.commit()
        return self.db.cur.rowcount > 0

    def count(self):
        self.db.cur.execute(f'SELECT COUNT(*) FROM {self.table}')
        return self.db.cur.fetchone()[0]


class Users(Table):
    table = 'users'
    columns = ('name', 'phone', 'password', 'role')
    users_db = {}


def register():
  print("\n--- Create New Account ---")
  username = input("Enter username: ").strip()

  if username in users_db:
    print(" Username already exists, please choose another one.")
    return

  password = input("Enter password: ").strip()
  if not username or not password:
    print(" Fields cannot be empty.")
    return

  users_db[username] = password
  print(" Account created successfully!")


def login():
  print("\n--- Login ---")
  username = input("Enter username: ").strip()
  password = input("Enter password: ").strip()

  if username in users_db and users_db[username] == password:
    print(f" Welcome {username}! Logged in successfully.")
    return True
  else:
    print("Incorrect username or password.")
    return False


def main():
  while True:
    print("\n====================")
    print("1. Register New Account")
    print("2. Login")
    print("3. Exit")
    print("====================")
users_db = {"ahmed": "12345", "sara": "pass2024"}


def reset_password():
  print("\n--- Reset Password ---")
  username = input("Enter username: ").strip()

 
  if username not in users_db:
    print(" Username does not exist!")
    return

  
  new_password = input("Enter new password: ").strip()

  if not new_password:
    print(" Password cannot be empty.")
    return


  users_db[username] = new_password
  print(" Password reset successfully")


class Movies(Table):
    table = 'movies'
    columns = ('title', 'genre', 'synopsis', 'actors', 'poster',
               'age_rating', 'rating', 'duration_minutes', 'release_date')


class Cinemas(Table):
    table = 'cinemas'
    columns = ('name', 'city', 'address')


class Halls(Table):
    table = 'halls'
    columns = ('cinema_id', 'name', 'hall_type', 'total_seats')


class Showtimes(Table):
    table = 'showtimes'
    columns = ('movie_id', 'hall_id', 'show_date', 'show_time', 'ticket_price')


class Food(Table):
    table = 'food'
    columns = ('name', 'size', 'price', 'quantity')


class Bookings(Table):
    table = 'bookings'
    columns = ('user_id', 'showtime_id', 'total_price', 'status')


class Tickets(Table):
    table = 'tickets'
    columns = ('booking_id', 'showtime_id', 'seat_number', 'price')


class BookingFood(Table):
    table = 'booking_food'
    columns = ('booking_id', 'food_id', 'quantity', 'price')


if __name__ == '__main__':
    db = Database()
    for table in (Users, Movies, Cinemas, Halls, Showtimes, Food, Bookings,
                  Tickets, BookingFood):
        print(f'{table.table}:', table(db).count())
    db.close()