import psycopg2
import jwt
import app
from models.vo import Account, Poll, Options, Vote, Category
from Exceptions import NoObjectFound, UnauthorizedAccess, ExceededVotes

conn = psycopg2.connect(
    host='localhost',
    database='poll',
    user='postgres',
    password='1234'
)

def verify_token(token):
    data = jwt.decode(token, app.app.config["SECRET_KEY"], algorithms=['HS256'])

    cursor = conn.cursor()
    account_sql = """
    SELECT * FROM ACCOUNT WHERE id = '{}';
    """.format(data["id"])
    
    cursor.execute(account_sql)
    current_user = cursor.fetchone()
    cursor.close()

    return current_user

def create_account(account):
    cursor = conn.cursor()
    account_sql = """
        INSERT INTO Account (name, email, username, password) VALUES ('{}', '{}', '{}', '{}')
        """.format(account.name, account.email, account.username, account.password)
    
    cursor.execute(account_sql)
    conn.commit()
    cursor.close()

def login(username, password):
    cursor = conn.cursor()
    account_sql ="""
        SELECT * FROM Account WHERE username = '{}' AND password = '{}';
        """.format(username, password)
    
    cursor.execute(account_sql)
    account = cursor.fetchone()
    if account:
        return account[0]

    cursor.close()


def account_polls(username):
    cursor = conn.cursor()

    account_sql = """
        SELECT account.id FROM Account WHERE username = '{}'
    """.format(username)

    cursor.execute(account_sql)
    account = cursor.fetchone()

    if account:
        polls_sql = """
            SELECT poll.*, 
            ARRAY_TO_STRING( ARRAY_AGG(Options.id|| ' ' || Options.optiontext), ',')
            FROM poll
            LEFT JOIN options ON poll.id = options.poll_id
            WHERE poll.account_id = '{}'
            GROUP BY poll.id;
        """.format(account[0])

        cursor.execute(polls_sql)
        current_poll = cursor.fetchone()

        polls_array = []

        while current_poll is not None:
            poll_object = Poll()
            poll_object.from_array(current_poll[:8])

            options_array = []
            options = current_poll[9].split(",")
            for option in options:
                if option != "":
                    option_split = option.split(" ")
                    option_object = Options(option_split[0], option_split[1], current_poll[0])
                    option_dic = option_object.get_json()
                    options_array.append(option_dic)
            
            poll_dic = poll_object.get_json()
            poll_dic["options"] = options_array
            polls_array.append(poll_dic)
            current_poll = cursor.fetchone()

        cursor.close()
        return polls_array
    else:
        raise NoObjectFound()


def create_poll(poll, options, user_id):
    cursor = conn.cursor()
    poll_sql = """
        INSERT INTO Poll (question, isclosed, ispublicstatistics, numchosenoptions, account_id) 
        VALUES ('{}', '{}', '{}', '{}', '{}') RETURNING id
        """.format(poll.get_json()["question"], poll.get_json()["isClosed"], poll.get_json()["isPublicStatistics"], 
        poll.get_json()["numChosenOptions"], user_id)

    cursor.execute(poll_sql)
    poll_id = cursor.fetchone()[0]

    for option in options:
        options_sql = """
            INSERT INTO Options (optiontext, poll_id) 
            VALUES ('{}', '{}')
            """.format(option["text"], poll_id)
        cursor.execute(options_sql)

    conn.commit()
    cursor.close()

def update_poll(data, account_id):
    cursor = conn.cursor()
    check = """
        SELECT * FROM Poll WHERE id = '{}' AND account_id = '{}'
        """.format(data["poll_id"], account_id)

    cursor.execute(check)
    if (cursor.fetchone()):
        
        poll_sql = """
        UPDATE Poll set isClosed = '{}', isPublicStatistics = '{}'
        WHERE id = '{}';
        """.format(data["isClosed"], data["isPublicStatistics"], data["poll_id"])

        cursor.execute(poll_sql)
    else:
        raise UnauthorizedAccess()
    
    conn.commit()
    cursor.close()

def latest():
    cursor = conn.cursor()
    poll_sql =  """
        SELECT poll.*, 
            ARRAY_TO_STRING( ARRAY_AGG(Options.id|| ' ' || Options.optiontext), ',')
            FROM poll
            LEFT JOIN options ON poll.id = options.poll_id
            GROUP BY poll.id
            ORDER BY created_at DESC;
        """

    cursor.execute(poll_sql)
    current_poll = cursor.fetchone()
    polls_array = []
    while current_poll is not None:
        poll_object = Poll()
        poll_object.from_array(current_poll[:8])

        options_array = []
        options = current_poll[9].split(",")
        for option in options:
            if option != "":
                option_split = option.split(" ")
                option_object = Options(option_split[0], option_split[1], current_poll[0])
                option_dic = option_object.get_json()
                options_array.append(option_dic)
            
        poll_dic = poll_object.get_json()
        poll_dic["options"] = options_array
        polls_array.append(poll_dic)
        current_poll = cursor.fetchone()

    cursor.close()
    return polls_array

def polls_result(poll_id, user_id):
    cursor = conn.cursor()
    
    check_sql = """
        SELECT isPublicStatistics, account_id FROM Poll
        WHERE id = '{}';
        """.format(poll_id)

    cursor.execute(check_sql)
    poll = cursor.fetchone()

    if poll:
        if poll[0] == False and poll[1] != user_id:
            raise UnauthorizedAccess()
        else:
            poll_sql = """
                SELECT options.id, options.optiontext, COUNT(vote.id)
                FROM vote
                RIGHT JOIN options ON options.id = vote.option_id
                WHERE options.poll_id = '{}'
                GROUP BY options.id;
                """.format(poll_id) #return COUNT ( * ) ?

            cursor.execute(poll_sql)
            current_option = cursor.fetchone()
            options_array = []
            total = 0

            while current_option is not None:
                option_dic = {}
                option_dic["id"] = current_option[0]
                option_dic["text"] = current_option[1]
                option_dic["count"] = current_option[2]
                total += option_dic["count"]
                options_array.append(option_dic)
                current_option = cursor.fetchone()

    else:
        raise NoObjectFound()

    cursor.close()
    return {"options": options_array, "total": str(total)}
    

def vote(data, user_id):
    cursor = conn.cursor()

    check_sql = """
        SELECT poll.id FROM Poll WHERE id = {}
    """.format(data["poll_id"])

    cursor.execute(check_sql)
    
    if (cursor.fetchone()):
        if (user_id != 0):
            vote_sql = """
                    INSERT INTO vote (poll_id, option_id, account_id)
                    SELECT {}, {}, {}
                    FROM vote
                    JOIN poll ON vote.poll_id = poll.id
                    WHERE poll.id = {} AND poll.timeLimit > CURRENT_TIMESTAMP AND vote.account_id = {}
                    GROUP BY vote.account_id, poll.limit_vote_per_user
                    HAVING COUNT (*) < poll.limit_vote_per_user;
                    """.format(data["poll_id"], data["option_id"], user_id, data["poll_id"], user_id)

            cursor.execute(vote_sql)
            if (cursor.fetchone() == None):
                raise ExceededVotes()
        else:
            vote_sql =  """
            INSERT INTO vote (poll_id, option_id)
            SELECT {}, {}
            FROM poll
            WHERE poll.id = 19 AND poll.timeLimit > CURRENT_TIMESTAMP;
            """.format(data["poll_id"], data["option_id"])
        
        cursor.execute(vote_sql)
    else:
        raise NoObjectFound()

    conn.commit()
    cursor.close()


def category(category_name):
    cursor = conn.cursor()

    check_sql = "SELECT id FROM Category WHERE categoryname = '{}'".format(category_name)

    cursor.execute(check_sql)
    poll_id = cursor.fetchone()

    if poll_id:
        poll_sql = """
            SELECT poll.*, 
            ARRAY_TO_STRING( ARRAY_AGG(Options.id|| ' ' || Options.optiontext), ',')
            FROM poll
            LEFT JOIN options ON poll.id = options.poll_id
            JOIN categorypoll ON poll.id = categorypoll.poll_id
            JOIN category ON category.id = categorypoll.category_id
            WHERE category.id = {}
            GROUP BY poll.id
            ORDER BY created_at DESC;
        """.format(poll_id[0])

        cursor.execute(poll_sql)
        current_poll = cursor.fetchone()
        polls_array = []
        while current_poll is not None:
            poll_object = Poll()
            poll_object.from_array(current_poll[:8])

            options = current_poll[9].split(",")
                
            poll_dic = poll_object.get_json()
            poll_dic["options"] = options_array
            polls_array.append(poll_dic)
            current_poll = cursor.fetchone()


    else:
        raise NoObjectFound()

    
    cursor.close()
    return polls_array