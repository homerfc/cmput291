import sys
import cx_Oracle
import random
import datetime
import re


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

def logout():
    global USR
    global PWD

    print("\nYou are logout successfuly.")
    USR = 0
    PWD = 0
    login_scrn()

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
        search_for_tweets()
    elif comm == '2':
        search_for_user()
    elif comm == '3':
        compose_tweet(USR)
    elif comm == '4':
        list_Followers(USR)
    elif comm == '5':
        logout()
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
    global CONNECTION

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
    global CONNECTION

    print("Select a user to see more details:")
    detail = input()
    try:
        flwrnumtw = ("SELECT COUNT(tid) FROM tweets WHERE writer = :detail")
        flwrnumfol = ("SELECT COUNT(flwee) FROM follows WHERE flwer = :detail")
        flwrnumflwr = ("SELECT COUNT(flwer) FROM follows where flwee = :detail")

        curs = CONNECTION.cursor()
        curs.execute(flwrnumtw, detail = detail)
        numtw = curs.fetchall()

        curs.execute(flwrnumfol, detail = detail)
        numfol = curs.fetchall()

        curs.execute(flwrnumflwr, detail = detail)
        numflwr = curs.fetchall()

        print('User:', detail, '|', 'Number of tweets:', numtw[0][0], '|',
        'Number of followees:', numfol[0][0], '|', 'Number of followers:', numflwr[0][0])
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
            list_Followers(USR)
        else:
            list_Followers(USR)
    elif comm == '2':
        follow_user(idofusr)

        list_Followers(USR)
    else:
        list_Followers(USR)

def follow_user(usrtofollow):
    global USR
    global CONNECTION


    try:
        follow = "INSERT INTO follows(flwer, flwee, start_date) values (:USR, :usrtofollow, sysdate)"

        curs = CONNECTION.cursor()
        curs.execute(follow, {'USR':USR, 'usrtofollow':usrtofollow})
        CONNECTION.commit()
        curs.close()
        print("You are following the user now.\n")

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        if error.code == 1:
            print('Sorry, you are following this user already.\n')
        else:
            print(sys.stderr, "Oracle code:", error.code)
            print(sys.stderr, "Oracle message:", error.message)


def search_for_tweets():
    #keyword should be a list of keyword i.e keyword = ["string", "string2",...]
    #access the hashtage table and tweets table for the hashtag and tweet content

    global CONNECTION
    global USR

    print("Enter the keyword w/o or w/ hashtag #, separate by dots:")
    keyword = input()
    try:
        matched_tweets = ("SELECT tid, tdate, text FROM tweets WHERE lower(text) LIKE lower('%'|| :keyword || '%') ORDER BY tdate")
        curs = CONNECTION.cursor()
        curs.execute(matched_tweets, keyword = keyword)
        display_tweet = curs.fetchmany(5)
        swt = True

        while swt:
            endmsg = "Sorry, we have reached the end."
            if len(display_tweet) == 0:
                print('')
                print(endmsg)
                swt = False
            else:
                for i in display_tweet:
                    print(i[0], "|", i[1].strftime('%d-%b-%Y'), "|", i[2], "|")
            display_tweet = curs.fetchmany(numRows = 5)
            if len(display_tweet) == 0:
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

        tweets_menu()

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)



def tweets_menu():
    options = input("\nSelect for more actions:\n1.More details about a tweet\n2.Compose reply\n3.Retweet\n4.Log out\n5.Return to the main menu\n")

    global CONNECTION
    global USR

    if options == '1':
        details_tweets = input("Select one tweet to see more details via entering tweet id:\n")
        tweets_statistics(details_tweets)
    elif options == '2':
        compose_tweet(USR)
    elif options == '3':
        retweet(USR)
    elif options == '4':
        logout()
    elif options == '5':
        main_menu()
    else:
        tweets_menu()

def tweets_statistics(tid):

    global CONNECTION
    global USR

    try:
        tweets_statistics = ("SELECT COUNT(r.tid), COUNT(t.tid) FROM tweets t, retweets r WHERE r.tid = :tid and t.replyto = :tid")
        curs = CONNECTION.cursor()
        curs.execute(tweets_statistics,(tid,tid))
        display_tweets_statistics = curs.fetchall()
        print("Retweets", '\t', 'Replies')
        for row in display_tweets_statistics:
            print(row[0], "\t\t", row[1])


        curs.close()
        tweets_menu()

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)


#checked
def retweet(usr):

    global CONNECTION
    global USR

    try:
        tid = input("Enter the tweet id that you want to retweet:\n")
        twid = random.randint(0, 10000)
        curs = CONNECTION.cursor()
        retweets = ("INSERT INTO retweets(usr,tid,rdate) VALUES (:USR, :tid, sysdate)")
        tweets = ("INSERT INTO tweets VALUES (:twid, :writer, sysdate, (SELECT text FROM tweets where tid = :tid), null)")


        curs.execute(retweets, {'USR':USR, 'tid':tid})
        curs.execute(tweets, {'twid':twid, 'writer':USR, 'tid':tid})
        CONNECTION.commit()

        print("Successfully retweeted!")
        curs.close()
        tweets_menu()

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        if error.code == 1:
            print('Sorry, you have already retweeted this tweet.\n')
            tweets_menu()
        else:
            print(sys.stderr, "Oracle code:", error.code)
            print(sys.stderr, "Oracle message:", error.message)

        raise

def compose_tweet(usr):

    global CONNECTION
    global USR

    try:
        message = input("Enter the tweet message: ")
        print("if this is reply, input whom you gonna reply; if this is new tweet, just press enter: ")
        replyto = input()
        compose_tweet = "INSERT INTO tweets (tid,writer,tdate,text,replyto) VALUES (:tid, :writer, sysdate, :text, :replyto)"
        terms = "SELECT term FROM hashtags"

        tid = crt_new_tid() #####same as create new user_id
        curs = CONNECTION.cursor()
        curs.execute(terms)
        lterms = curs.fetchall()
        ltermsfixed = []
        test = []
        for i in lterms:
            ltermsfixed.append(i[0])
        for i in ltermsfixed:
            test.append(i.rstrip())

        print(test)

        curs.execute(compose_tweet, {'tid':tid, 'writer':USR, 'text':message, 'replyto':replyto})

        print("Tweet successfully!")

        message_in_list = message.split()

        hashtag = []
        hashtags = []

        for i in message_in_list:
            if (re.match("#.*$",i)):
                hashtag.append(i)

        for i in hashtag:
            hashtags.append(i.replace('#',''))

        upd_hashtags = "INSERT INTO hashtags (term) VALUES (:term)"
        upd_mentions = "INSERT INTO mentions (tid, term) VALUES (:tid, :term)"

        if len(hashtag) > 0:
            for i in hashtags:
                if i not in test:
                    curs.execute(upd_hashtags, {'term':i})
            for i in hashtags:
                curs.execute(upd_mentions, {'tid':tid, 'term':i})
        else:
            pass

        CONNECTION.commit()
        curs.close()
        main_menu()

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)


def crt_new_tid():
    random.seed()
    tid = random.randint(0, 10000)
    if check_uniq_tid(tid):
        crt_new_tid()
    else:
        return tid

def check_uniq_tid(tid):

    global CONNECTION

    checkUniq = "SELECT tid FROM tweets WHERE tid = :tid"
    curs = CONNECTION.cursor()
    curs.execute(checkUniq, tid = tid)
    cnt = len(curs.fetchall())
    if cnt > 0:
        curs.close()
        return True
    else:
        return False

def search_for_user():

    global CONNECTION


    try:
        print('Enter the keyword to search.\n')
        keyword = input()
        swt = True
        curs = CONNECTION.cursor()

        extract_name = "SELECT usr, name FROM users where lower(name) LIKE lower('%'||:keyword_name||'%') ORDER BY LENGTH(name)"
        curs.execute(extract_name, keyword_name = keyword)
        row_from_keyword_name = curs.fetchmany(5)

        extract_city = "SELECT usr, name FROM users where lower(city) LIKE lower('%'||:keyword_city||'%') ORDER BY LENGTH(city)"
        curs.execute(extract_city, keyword_city = keyword)
        row_from_keyword_city = curs.fetchmany(5)


        while swt:
            endmsg = "Sorry, we have reached the end."
            noresult = "Sorry, we could not find anything."
            if len(row_from_keyword_name) == 0 and len(row_from_keyword_city) == 0:
                print('')
                print(noresult)
                swt = False
            else:
                print("----Match by Name----")
                for row in row_from_keyword_name:
                    print(row[0], row[1])
                print("----Match by City----")
                for row in row_from_keyword_city:
                    print(row[0], row[1])
            row_from_keyword_name = curs.fetchmany(5)
            row_from_keyword_city = curs.fetchmany(5)
            if len(row_from_keyword_name) == 0 and len(row_from_keyword_city) == 0:
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

        see_more_information()

        main_menu()

        curs.close()

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)

def see_more_information():

    global CONNECTION

    options = input("Select for more actions:\
                    \n1.More details about user\
                    \n2.Follow the user\
                    \n3.Back to main menu\
                    \n4.Back to search.")
    if (options == '1'):
        u_see_more_details()
    elif(options == '2'):
        follow_user()
    elif(options == '3'):
        main_menu()
    elif(options == '4'):
        search_for_user()
    else:
        print("Invalid Command.")
        see_more_information(USR)   #return to the main menu

def u_see_more_details():
    global CONNECTION

    print("Select a user to see more details:")
    detail = input()
    try:
        flwrnumtw = ("SELECT COUNT(tid) FROM tweets WHERE writer = :detail")
        flwrnumfol = ("SELECT COUNT(flwee) FROM follows WHERE flwer = :detail")
        flwrnumflwr = ("SELECT COUNT(flwer) FROM follows where flwee = :detail")

        curs = CONNECTION.cursor()
        curs.execute(flwrnumtw, detail = detail)
        numtw = curs.fetchall()

        curs.execute(flwrnumfol, detail = detail)
        numfol = curs.fetchall()

        curs.execute(flwrnumflwr, detail = detail)
        numflwr = curs.fetchall()

        print('User:', detail, '|', 'Number of tweets:', numtw[0][0], '|',
        'Number of followees:', numfol[0][0], '|', 'Number of followers:', numflwr[0][0])

        u_see_more_tweets(detail)

        curs.close()

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args

        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)

def u_see_more_tweets(idofusr):
    global CONNECTION
    global USR

    flwer3tweets = "SELECT tid, text FROM tweets WHERE writer = :detail ORDER BY tdate"

    curs = CONNECTION.cursor()
    curs.execute(flwer3tweets, detail = idofusr)
    tweets = curs.fetchmany(3)

    for row in tweets:
        print(row[0], '|', row[1])

    print('What do you want to do next?\n1.See more tweets of the user\n2.Follow the user\n3.Return to the previous menu')
    comm = input()

    if comm == '1':
        while len(tweets) > 0:
            tweets = curs.fetchmany(3)
            for row in tweets:
                print(row[0], '|', row[1])
        print('No more tweets.')
        print('1.Return to the previous menu\n2.Follow the user')
        comm2 = input()
        if comm2 == '2':
            follow_user(idofusr)
            see_more_information()
        else:
            see_more_information()
    elif comm == '2':
        follow_user(idofusr)
        see_more_information()
    else:
        see_more_information()


def main():
    global USR
    global PWD
    global CONNECTION

    connstr = "lebedev/23048424S@gwynne.cs.ualberta.ca:1521/CRS"

    CONNECTION = cx_Oracle.connect(connstr)

    login_scrn()

    CONNECTION.close()


main()
