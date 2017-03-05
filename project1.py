import sys
import cx_Oracle
import random
import datetime


global USR
global PWD

#login and signup, check for user id and password
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
        print('')
        print("Login is successful.")
        print('')
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

#creates new account and insert the info to the database
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

def main_menu():
    line = "______________________________________"
    print(line)
    mainmenu = "What do you want to do next?"
    print(mainmenu)
    menu = ["1 - Search for tweets", "2 - Search for users", "3 - Write a tweet", "4 - Followers", "5 - Logout"]
    for com in menu:
        print(com)

#displays the last 5 tweets of the user
def tweet_scrn(connection):
    global USR
    global PWD

    getTweets = ("SELECT distinct t.writer, t.tdate, t.text FROM tweets t "
    "WHERE t.writer in (select f.flwee from follows f where f.flwer = :USR) ORDER BY tdate")

    curs = connection.cursor()
    curs.execute(getTweets, USR=USR)
    rows = curs.fetchmany(numRows = 5)
    swt = True

    while swt:
        endmsg = "Sorry, we have reached the end of your feed."
        if len(rows) == 0:
            print('')
            print(endmsg)
            swt = False
        else:
            for i in rows:
                print(i[0], "|", i[1].strftime('%d-%b-%Y'), "|", i[2], "|")
        rows = curs.fetchmany(numRows = 5)
        if len(rows) == 0:
            print('')
            print(endmsg)
            swt = False
        else:
            print("Do you want to see more? Yes or no:")
            comm = input()
            comm.lower()
            if comm in ('yes', 'y'):
                continue
            else:
                print('')
                print(endmsg)
                swt = False

    curs.close()
    main_menu() #function of choises


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
