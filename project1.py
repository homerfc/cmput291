import sys
import cx_Oracle
import random


global USR
global PWD

#main menu, check for user id and password
def login_scrn(connection):
    global USR
    global PWD

    command = input('Type 1 to Log in. Type 2 to create New account. Type 3 to exit.')

    if command == '1':
        print("Login:")
        USR = input()
        print("Password:")
        PWD = input()
    elif command == '2':
        print("Let's create a new account for you.")
        crt_new_acc(connection)
    elif command == '3':
        exit()
    else:
        login_scrn()

    checkUsr = "SELECT usr, pwd FROM users WHERE usr=:USR and pwd=:PWD"

    curs = connection.cursor()
    curs.execute(checkUsr, USR=USR, PWD=PWD)

    cnt = len(curs.fetchall())
    if cnt > 0:
        print("Login is successful.")
    else:
        print("Password is incorrect.")
        login_scrn(connection)
    curs.close()

#check the password for uniqness
def check_uniq(connection, usrid):
    checkUniq = "SELECT usr FROM users WHERE usr = :usrid"

    curs = connection.cursor()
    curs.execute(checkUniq, usrid = usrid)
    cnt = len(curs.fetchall())
    if cnt > 0:
        print("User id is exist. Pick another ID.")
        curs.close()
        return True
    else:
        return False

#creates new account and insert the info to database
def crt_new_acc(connection):
    random.seed()
    usrid = random.randint(0, 10000)
    print("Your user ID will be: " + str(usrid))
    if check_uniq(connection, usrid):
        print("This user ID is already exist. We will generate a new one.")
        crt_new_acc(connection)
    else:
        print("Now we need a bit of personal info.")
        print("Name:")
        name = input()
        print("Password (4 characters long):")
        pwd = input()
        print("Email:")
        email = input()
        print("City:")
        city = input()
        print("Timezone:")
        tmzn = input()
        print("Great! Please save your ID and password. You will need it to sign in.")
        insertNewUsr = "INSERT INTO users VALUES (:1, :2, :3, :4, :5, :6)"
        curs = connection.cursor()
        curs.execute(insertNewUsr, (usrid, pwd, name, email, city, tmzn))
        connection.commit()
        curs.close()
        login_scrn(connection)

#displays the last 5 tweets of the user
def tweet_scrn(connection):
    global USR
    global PWD

    getTweets = "SELECT text FROM tweets WHERE writer = :USR ORDER BY tdate"

    curs = connection.cursor()
    curs.execute(getTweets, USR=USR)
    rows = curs.fetchall()
    print("Your fresh tweets:")
    for row in rows:
        print(row)
    curs.close()


def main():
    global USR
    global PWD

    connstr = "lebedev/23048424S@gwynne.cs.ualberta.ca:1521/CRS"

    try:
        connection = cx_Oracle.connect(connstr)

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)

    login_scrn(connection)

    tweet_scrn(connection)

    connection.close()


main()
