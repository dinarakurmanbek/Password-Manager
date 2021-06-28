
# erfordeliche Module
import sys
import sqlite3
import time
import random
import pyperclip
from datetime import datetime
import getpass

# globale Datenbank (mit master passwort) in Ubuntu ausführen zu können
passman_db = "passman.db"

'''bei jeder nachfolgenden Funktion wird Differenz datetime.now()-Funktion mit dem Zeitpunkt der letzten Passworteingabe(t1-Variable) berechnet und 
   wenn 5 Minuten vergangen sind, wird die ask_password()-Funktion aufgerufen'''

def check_doable(db_name):
    conn = sqlite3.connect(passman_db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM dbs WHERE db_name=?", (db_name,))
    result = cur.fetchone()
    last_password_input = result[2]
    timer = 300  # in seconds; 5 min = 300

    t1 = datetime.strptime(last_password_input, "%b %d %H:%M:%S %Y")
    nowstr = datetime.now().strftime("%b %d %H:%M:%S %Y")
    t2 = datetime.strptime(nowstr, "%b %d %H:%M:%S %Y")

    diff = (t2 - t1).total_seconds()

    if diff < timer:
        print("Still in time: allow running the command")
    else:
        print("5 min over: do not allow the command.")
        ask_password(db_name)

"""in dieser Funktion wird Master-Password wiederholt abgefragt und wenn Master-Password richtig eingetragen ist, 
   wird mit cur.execute()-Methode, die in if-Anweisung sich befindet, die Zeitspanne aktualisiert"""

def ask_password(db_name):
    while True:
        master_password = getpass.getpass("Repeat your master password: ")
        conn = sqlite3.connect(passman_db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM dbs WHERE db_name=?", (db_name,))
        result = cur.fetchone()

        if result[1] == master_password:
            print('Password correct, updating timestamp.')
            dt = datetime.now().strftime("%b %d %H:%M:%S %Y")
            cur.execute("UPDATE dbs SET dt = ?", (dt,))
            conn.commit()
            break
        else:
            print('Password is wrong, aborting...')

'''Mit if-Anweisung wird geringste Anzahl von erforderlichen Argumenten geprüft: 
operation = sys.argv[1], db_name = sys.argv[2], title = sys.argv[3], username = sys.argv[4], password = sys.argv[5].
z.B. python passman.py(Projectname) add(operation) database(db_name) moodle(title) musterman(username) superpass123(password)'''
if len(sys.argv) < 2:
    str = "Not enough arguments provided"
    print(str)
    exit()

'''mit dem Befehlszeilenargument kann man Datenbank erstellen, in DB Eintraege eingeben und speichern, Eintraege als Tabelle darstellen, 
   von DB Einträge löschen, Passwörter generiren und von Einträgen das Password in Zwischenablage speichern '''
operation = sys.argv[1]

'''Datenbank in der globalen DB passman.db, durch die kann man mit bestimmten Einträgen manipuliren und zugreifen'''
db_name = sys.argv[2]

"""dieser Befehl wird benötigt, um eine DB fuer Einträge zu erstellen. Beim Erstellen wird Master Password initialisiert. 
Master Password wird 2 mal eingegeben, damit wird Übereinstimmung des Passworts geprüft, wenn nicht wird DB nicht erstellt. 
Ansonsten wird DB mit Name der DB, Master-Passwort und Zeitpunkt, der letzten Passworteingabe erzeugt  
Außerdem wird eine Tabelle mit Atributen wie:Titel, Username und Password angelegt """

if operation == 'create-database':
    print('Creating Database')
    master_pw = getpass.getpass("Enter master password: ")
    second_input = getpass.getpass("Repeat master password: ")
    if master_pw != second_input:
        print("Passwords are not equals, aborting..")
        exit()
    conn = sqlite3.connect(passman_db)
    cur = conn.cursor()

    dt = datetime.now().strftime("%b %d %H:%M:%S %Y")
    cur.execute("INSERT or IGNORE INTO dbs VALUES(?, ?, ?);", (db_name, master_pw, dt))
    conn.commit()
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS passwords(
        title TEXT PRIMARY KEY,
        username TEXT,
        password TEXT);
    """)
    conn.commit()
    print("Database was successfully created")

'''dieser Befehl ändert Master-Password in der globalen DB.
   Zur Kontrolle wird zunächst altes Passwort gefragt, nach der richtigen Eingabe wird die Möglichkeit gegeben 
   neues Master-Passwort einzugeben. Nach der Eingabe des neuen Passworts wird Master-Passwort in DB aktualisiert'''

if operation == 'change':
    check_doable(db_name)
    while True:
        old_pass = getpass.getpass("Enter your old master password: ")
        conn = sqlite3.connect(passman_db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM dbs WHERE db_name=?", (db_name,))
        result = cur.fetchone()
        if result[1] != old_pass:
            print("Wrong password...Try again")
        else:
            new_pass = getpass.getpass("Enter your new master password: ")
            conn = sqlite3.connect(passman_db)
            cur = conn.cursor()
            cur.execute("SELECT * FROM dbs WHERE db_name=?", (db_name,))
            result = cur.fetchone()
            if result[1] != new_pass:
                print('Your password was updated')
                cur.execute("UPDATE dbs SET  master_pw= ?", (new_pass,))
                dt = datetime.now().strftime("%b %d %H:%M:%S %Y")
                cur.execute("UPDATE dbs SET dt = ?", (dt,))
                conn.commit()
                break
            else:
                print('New password is same as your old password')
                exit()

'''mit dieser Funktion  werden verschiedene Optionen wie: Länge, Groß-/Kleinschreibung, Sonderzeichen/Symbole von Benutzer bestimmt,
   für weitere Generirung des Passworts. Mit While-Schleifen und try except-Konstrukten werden alle  Fehlereingaben berücksichtigt.
   Programm fordert password_length >= 8 an'''

def password_parameters():
    while True:
        password_length = input("How long would your password need to be (at least 8 characters): ")  # 8
        if password_length != int:
            try:
                if int(password_length) >= 8:
                    password_length1 = int(password_length)
                    break
            except ValueError:
                print("Parameters need to be an digit, try again...")

    while True:
        upper = input("Amount of upper case letters: ")
        if upper != int:
            try:
                upper1 = int(upper)
                break
            except ValueError:
                print("Parameters need to be an digit, try again...")

    while True:
        lower = input("Amount of lower case letters: ")
        if lower != int:
            try:
                lower1 = int(lower)
                break
            except ValueError:
                print("Parameters need to be an digit, try again...")

    while True:
        spec = input("Amount of special characters: ")
        if spec != int:
            try:
                spec1 = int(spec)
                break
            except ValueError:
                print("Parameters need to be an digit, try again...")

    while True:
        num = input("Amount of numbers: ")
        if num != int:
            try:
                num1 = int(num)
                break
            except ValueError:
                print("Parameters need to be an digit, try again...")

    if password_length1 == (upper1 + lower1 + spec1 + num1):
        return password_generator(password_length1, upper1, lower1, spec1, num1)
    else:
        print("Your entered number of characters does not match with password length!")
        password_parameters()

'''in diese Funktion wird mit Hilfe char-Variablen ein Passwort erstellt 
Mit Hilfe random.choise-Methode werden zufällige Symbole von char-Variablen in for-Schleife ausgewählt und 
mit join()-Methode verbindet und zu einem Passwort gebildet.'''

def password_generator(password_length1, upper1, lower1, spec1, num1):
    password = ""
    char1 = "abcdefghijklmnopqrstuvwxyz"
    char2 = char1.upper()
    char3 = "0123456789"
    char4 = "@'%&*()?.-" # mache Zeichen werden in Programm nicht erkannt und sind von uns weggelassen(!'#$)

    for x in range(password_length1):
        if password == password_length1:
            return password
        for i in range(upper1):
            password += random.choice(char2)
        for j in range(lower1):
            password += random.choice(char1)
        for k in range(spec1):
            password += random.choice(char4)
        for l in range(num1):
            password += random.choice(char3)
        pass_word = list(password)
        password = "".join(pass_word)
        return password

'''mit dem Befehl "generate" werden Passwörter zufällig generiert und es gibt eine Option mit Zustimmung des Benutzers,
   dieses Passwort in Zwischenablage zu speichern.'''

if operation == 'generate':
    #num_of_chars = random.randint(8, 20)
    password = password_parameters()
    print("Hier is your password: ", password)
    answer_genpass = input("Do you want copy this password: [y]es or [n]o ") # erste Funktion, die generierte Password copiert
    if answer_genpass == "y".upper() or answer_genpass == "y":
        pyperclip.copy(password)
        print("Copied in Clipboard")
    else:
        print("This password was not copied")

'''dieser Befehl wird benötigt um Einträge in die Tabelle hinzuzufügen, 
bei der Eingabe müssen der Name der DB und Daten von Einträgen: Titel, Username und Password angegeben werden
Bei der Passworteingabe muss es in Anführungszeichen gesetzt werden'''

if operation == 'add':
    check_doable(db_name)
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    title = sys.argv[3]
    username = sys.argv[4]
    password = sys.argv[5]
    entry = (title, username, password)
    cur.execute("INSERT INTO passwords VALUES(?, ?, ?);", entry)
    conn.commit()
    print("Your entry was added")

'''dieser Befehl wird benötigt um alle Eintraege von DB rauszuholen, dafür ist fetchall() Methode verantwortlich, 
und mit for-Schleife als eine Tabelle darzustellen'''

if operation == 'list':
    check_doable(db_name)
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("SELECT * FROM passwords;")
    result = cur.fetchall()
    print("\n                                                        <ALL SAVED PASSWORDS>")
    print(
        " ----------------------------------------------------------------------------------------------------------------------------------------------")
    print(
        "|             -----TITLE-----              |                -----USERNAME-----               |                -----PASSWORD-----               |")
    print(
        " ----------------------------------------------------------------------------------------------------------------------------------------------")
    for x in result:
        print("|" + x[0], " " * (40 - len(x[0])), "|",
              x[1], " " * (46 - len(x[1])), "|",
              x[2], " " * (46 - len(x[2])), "|")

'''dieser Befehl wird benötigt um gewählte Einträge von der Tabelle zu löschen, bei der Eingabe müssen der Name der DB und Titel angegeben werden, 
   aber es wird um eine Bestätigung mit input()-Funktion nachgefragt'''

if operation == 'delete':
    check_doable(db_name)
    title = sys.argv[3]
    answer = input("Are you sure you want delete entry <" + title + "> [y]es or [n]o: ")
    if answer != "y":
        print("Your entry was not deleted")
        exit()
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute('DELETE FROM passwords WHERE title=?', (title,))
    conn.commit()
    print("Your entry was successfully deleted")


'''mit dem Befehl "get" kopiert man das Passwort in Zwischenablage.
   Bei der Eingabe des Befehls muss man den Namen der DB und Titel von dem Eintrag eintippen.
   Danach wird ausgewähltes Password in Clipboard kopiert und man kann z.B in einer Webseite einfügen. 
   time.sleep()-Funktion verzögert Programm für 15 Sekunden, nach dieser Zeit wird die Zwischenablage geleert'''

if operation == 'get':
    print("Copied in Clipboard. You have 15 sec to paste your password")
    check_doable(db_name)
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("SELECT * FROM passwords WHERE title=?", (sys.argv[3],))
    result = cur.fetchone()
    pyperclip.copy(result[2])
    time.sleep(15)
    pyperclip.copy('')

