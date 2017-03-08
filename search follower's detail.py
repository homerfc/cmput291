
def list_Followers(usrID):
    global connection

    try:

        follower = "SELECT flwer FROM follows WHERE flwee =:usrID"
        curs = CONNECTION.cursor()

        curs.execute(follower, usrID = usrID)
        rows = fetchall()
        for row in rows:
            print(row)
        options = input("Select for more actions:\n1:more details about follower\n2:see more tweets\n3:follow the selected user\n:")

        if options == 1:
            see_more_details()
        elif options == 2:
            see_more_tweets()
        elif options == 3:
            start_to_follow(usrID)
        else:
            return list_Followers(usrID)   #return to the main menu)

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)


def see_more_details():
    global connection
    detail = input("Select one follower to see more details")

    try:
        flwerdtl = ("SELECT COUNT(t.tid) FROM tweets t WHERE t.writer = :detail "
        "UNION SELECT COUNT(f.flwee) FROM follows f WHERE f.flwer = :detail UNION SELECT COUNT(f.flwer) "
        "FROM follows f where f.flwee = :detail")
        flwer3tweets = "SELECT tid, text FROM tweets WHERE writer = :detail ORDER BY tdate"

        curs = CONNECTION.cursor()
        curs.execute(flwerdtl, detail = detail)
        details = curs.fetchall()

        print('User:', detail, '|', 'Number of tweets:', details[0],
        'Number of followees:', details[1], 'Number of followers:', details[2])

        curs.execute(flwer3tweets, detail = detail)
        tweets = fetchmany(3)

        for row in tweets:
            print(row[0], '|', row[1])

        curs.close()

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)


def see_more_tweets():
    try:
        more_tweets = input("enter number to see more user's tweet")
        if (more_tweets!=0):
            tweets = fetchmany(more_tweets+3)
            for tweets_row in tweets:
                print(tweets_row)
        else:
            for tweets_row in tweets:
                print(tweets_row)

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)

def start_to_follow(usrID):
    try:
        start_to_follow = input("follow/unfollow")
        if (start_to_follow == "follow"):
            following = "insert into follows (flwer, flwee, start_date) value (" +
                        usrID +","+ detail +", curdate);"
            curs.execute(following)
        else:
            return
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print(sys.stderr, "Oracle code:", error.code)
        print(sys.stderr, "Oracle message:", error.message)
