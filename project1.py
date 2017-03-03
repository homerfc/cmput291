import sys
import cx_Oracle


global USR
global PWD
global REG

def login_scrn():
    global USR
    global PWD

    command = input('Type 1 to Log in. Type 2 to create New account. Type 3 to exit.')

    if command == '1':
        print("Login:")
        USR = input()
        print("Password:")
        PWD = input()
    elif command == '2':
        print('Start registration.')
    elif command == '3':
        exit()
    else:
        login_scrn()

    connStr = "lebedev/23048424S@gwynne.cs.ualberta.ca:1521/CRS"
    checkUsr = "SELECT usr, pwd FROM users WHERE usr=:USR and pwd=:PWD"
    try:
        connection = cx_Oracle.connect(connStr)
        curs = connection.cursor()
        curs.execute(checkUsr, USR=USR, PWD=PWD)

        rows = curs.fetchone()
        if USR == rows[0] and PWD == rows[1]:
            print("Login is successful.")
        else:
            print("Login or password is incorrect.")


        curs.close()
        connection.close()

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args

        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)


def check_usr_pwd():
    connStr = "lebedev/23048424S@gwynne.cs.ualberta.ca:1521/CRS"
    checkUsr = "SELECT usr FROM users WHERE usr=:1 and pwd=:2"
    try:
        connection = cx_Oracle.connect(connStr)
        curs = connection.cursor()
        curs.execute(checkUsr, (USR, PWD))

        rows = curs.fetchall()
        print("Login is successful.")
        curs.close()
        connection.close()

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print("Login or password is incorrect.")

        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)


def tweetScrn():
    global USR
    global PWD

    connStr = "lebedev/23048424S@gwynne.cs.ualberta.ca:1521/CRS"
    getTweets = "SELECT text FROM tweets WHERE writer = :USR ORDER BY tdate"
    try:
        connection = cx_Oracle.connect(connStr)
        curs = connection.cursor()
        curs.execute(getTweets, USR=USR)
        rows = curs.fetchall()
        print("Your fresh tweets:")
        for row in rows:
            print(row)
        curs.close()
        connection.close()

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)


def main():
    global USR
    global PWD

    login_scrn()

    tweetScrn()


main()
