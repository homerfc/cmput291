import sys
import cx_Oracle
import random
import datetime


global USR
global PWD
global CONNECTION

#login and signup, check for user id and password
def login_scrn():
    global USR
    global PWD
    global CONNECTION

    command = input('Type 1 to Log in. Type 2 to create New account. Type 3 to exit.')

    if command == '1':
        print("Login:")
        USR = input()
        print("Password:")
        PWD = input()
    elif command == '2':
        print("Let's create a new account for you.")
        crt_new_acc()
    elif command == '3':
        exit()
    else:
        login_scrn()

    checkUsr = "SELECT usr, pwd FROM users WHERE usr=:USR and pwd=:PWD"

    curs = CONNECTION.cursor()
    curs.execute(checkUsr, USR=USR, PWD=PWD)

    cnt = len(curs.fetchall())
    if cnt > 0:
        print('')
        print("Login is successful.")
        print('')
        tweet_scrn()
    else:
        print("Password is incorrect.")
        login_scrn()
    curs.close()

#check the password for uniqness
def check_uniq(usrid):
    global CONNECTION

    checkUniq = "SELECT usr FROM users WHERE usr = :usrid"

    curs = CONNECTION.cursor()
    curs.execute(checkUniq, usrid = usrid)
    cnt = len(curs.fetchall())
    if cnt > 0:
        print("User id is exist. Pick another ID.")
        curs.close()
        return True
    else:
        return False

#creates new account and insert the info to the database
def crt_new_acc():
    global CONNECTION

    random.seed()
    usrid = random.randint(0, 10000)
    print("Your user ID will be: " + str(usrid))
    if check_uniq(usrid):
        print("This user ID is already exist. We will generate a new one.")
        crt_new_acc()
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
        curs = CONNECTION.cursor()
        curs.execute(insertNewUsr, (usrid, pwd, name, email, city, tmzn))
        CONNECTION.commit()
        curs.close()
        login_scrn()

def main_menu():
    global USR

    line = "______________________________________"
    print(line)
    mainmenu = "What do you want to do next?"
    print(mainmenu)
    menu = ["1 - Search for tweets", "2 - Search for users", "3 - Write a tweet", "4 - Followers", "5 - Logout"]
    for com in menu:
        print(com)
    comm = input()
    if comm == '1':
        pass
    elif comm == '2':
        print("Type your keyword to search:")
        keyword = input()
        search_for_tweets(keyword)
    elif comm == '3':
        pass
    elif comm == '4':
        list_Followers(USR)
    elif comm == '5':
        print("You are logout successfuly.")
        USR = 0
        PWD = 0
        login_scrn()

#displays the last 5 tweets of the user
def tweet_scrn():
    global USR
    global PWD
    global CONNECTION

    getTweets = ("SELECT distinct t.writer, t.tdate, t.text FROM tweets t "
    "WHERE t.writer in (select f.flwee from follows f where f.flwer = :USR) ORDER BY tdate")

    curs = CONNECTION.cursor()
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

def list_Followers(usrID):
    global connection

    try:

        follower = "SELECT f.flwer, u.name FROM follows f, users u WHERE flwee =:usrID and usr = f.flwer"
        curs = CONNECTION.cursor()

        curs.execute(follower, usrID = usrID)
        rows = curs.fetchall()
        if len(rows) == 0:
            print("Sorry, you don't have any followers and followees.")
        else:
            print("______________________________________")
            print('ID', '|', "Name")
            for row in rows:
                print(row[0], '|', row[1])
        print("______________________________________")

        print("Select for more actions\n1.More details about "
         "a follower\n2.Return to the main menu")
        options = input()
        if options == '1':
            see_more_details()
        elif options == '2':
            main_menu()  #return to the main menu)
        else:
            list_Followers(USR)

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)

def see_more_details():
    global connection

    print("Select one follower to see more details:")
    detail = input()
    try:
        flwerdtl = ("SELECT COUNT(t.tid) FROM tweets t WHERE t.writer = :detail "
        "UNION SELECT COUNT(f.flwee) FROM follows f WHERE f.flwer = :detail UNION SELECT COUNT(f.flwer) "
        "FROM follows f where f.flwee = :detail")


        curs = CONNECTION.cursor()
        curs.execute(flwerdtl, detail = detail)
        details = curs.fetchmany(numRows = 3)

        print('User:', detail, '|', 'Number of tweets:', details[2][0], '|',
        'Number of followees:', details[1][0], '|', 'Number of followers:', details[0][0])

        see_more_tweets(detail)

        curs.close()

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)

def see_more_tweets(idofusr):
    global CONNECTION
    global USR

    flwer3tweets = "SELECT tid, text FROM tweets WHERE writer = :detail ORDER BY tdate"

    curs = CONNECTION.cursor()
    curs.execute(flwer3tweets, detail = idofusr)
    tweets = curs.fetchmany(3)

    for row in tweets:
        print(row[0], '|', row[1])

    print('What do you want to do next?\n1.See more tweets of the user\n2.Follow the user\n3.Return to the list of followers')
    comm = input()

    if comm == '1':
        while len(tweets) > 0:
            tweets = curs.fetchmany(3)
            for row in tweets:
                print(row[0], '|', row[1])
        print('No more tweets.')
        print('1.Return to the list of followers\n2.Follow the user')
        comm2 = input()
        if comm2 == '2':
            follow_user(idofusr)
            print("You are following the user now.")
            list_Followers(USR)
        else:
            list_Followers(USR)
    elif comm == '2':
        follow_user(idofusr)
        print("You are following the user now.")
        list_Followers(USR)
    else:
        list_Followers(USR)

def follow_user(usrtofollow):
    global USR
    global CONNECTION

    d4te = datetime.datetime.now()

    follow = "INSERT INTO follows(flwer, flwee, start_date) values (:USR, :usrtofollow, to_date(:d4te, 'yyyy-mm-dd'))"

    curs = CONNECTION.cursor()
    curs.execute(follow, {'USR':USR, 'usrtofollow':usrtofollow, 'd4te':d4te })
    CONNECTION.commit()
    curs.close()

def main():
    global USR
    global PWD
    global CONNECTION

    connstr = "lebedev/23048424S@gwynne.cs.ualberta.ca:1521/CRS"

    try:
        CONNECTION = cx_Oracle.connect(connstr)

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)

    login_scrn()

    CONNECTION.close()


main()
