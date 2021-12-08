from .connect_database import getConnection
from models.vo.poll import Poll
from models.vo.exceptions import NoObjectFound, UnauthorizedAccess, ExceededVotes


class PollDAO:

    def create_poll(poll):
        conn = getConnection()
        cursor = conn.cursor()
        poll_sql = """
            INSERT INTO Poll (question, isclosed, ispublicstatistics, timeLimit, 
                            account_id, limit_vote_per_user) 
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """

        cursor.execute(poll_sql, (poll.question, poll.isClosed, poll.isPublicStatistics, 
            poll.timeLimit, poll.account_id, poll.limit_vote_per_user))

        poll_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()
        
        return poll_id

    def update_poll(poll):
        conn = getConnection()
        cursor = conn.cursor()
        check = """
            SELECT * FROM Poll WHERE id = %s AND account_id = %s
            """

        cursor.execute(check, (poll.id, poll.account_id))

        if (cursor.fetchone()):
            
            poll_sql = """
            UPDATE Poll set isClosed = %s, isPublicStatistics = %s, timeLimit = %s, limit_vote_per_user = %s
            WHERE id = %s;
            """

            cursor.execute(poll_sql, (poll.isClosed, poll.isPublicStatistics, poll.timeLimit, 
                        poll.limit_vote_per_user, poll.id))
        else:
            raise UnauthorizedAccess()
        
        conn.commit()
        cursor.close()
        conn.close()

    def latest():
        conn = getConnection()
        cursor = conn.cursor()
        poll_sql =  """
            SELECT * FROM poll ORDER BY created_at DESC;
            """

        cursor.execute(poll_sql)
        current_poll = cursor.fetchone()
        polls_array = []
        while current_poll is not None:
            poll_object = Poll(id= current_poll[0], question= current_poll[1], isClosed= current_poll[2],
                            isPublicStatistics= current_poll[3], numChosenOptions= current_poll[4], 
                            timeLimit= current_poll[5], account_id= current_poll[6], created_at= current_poll[7], limit_vote_per_user= current_poll[0])
                
            poll_dic = poll_object.get_json()
            polls_array.append(poll_dic)
            current_poll = cursor.fetchone()

        cursor.close()
        conn.close()

        return polls_array

    def delete_poll(id, account_id):
        conn = getConnection()
        cursor = conn.cursor()

        account_sql = """
            DELETE FROM Poll WHERE id=%s AND account_id=%s
        """

        cursor.execute(account_sql, (id,account_id))
        
        conn.commit()
        cursor.close()
        conn.close()

    def account_polls(username):
        conn = getConnection()
        cursor = conn.cursor()

        account_sql = """
            SELECT account.id FROM Account WHERE username = %s
        """

        cursor.execute(account_sql, (username,))
        account = cursor.fetchone()

        if account:
            polls_sql = """
                SELECT * FROM poll
                WHERE poll.account_id = %s
            """

            cursor.execute(polls_sql, (account[0],))
            current_poll = cursor.fetchone()

            polls_array = []

            while current_poll is not None:
                poll_object = Poll(id= current_poll[0], question= current_poll[1], isClosed= current_poll[2],
                            isPublicStatistics= current_poll[3], numChosenOptions= current_poll[4], 
                            timeLimit= current_poll[5], account_id= current_poll[6], created_at= current_poll[7], limit_vote_per_user= current_poll[0])
                
                poll_dic = poll_object.get_json()
                polls_array.append(poll_dic)
                current_poll = cursor.fetchone()

            cursor.close()
            conn.close()

            return polls_array
        else:
            raise NoObjectFound()


    def checkResultAuthorization(poll_id, user_id):
        conn = getConnection()
        cursor = conn.cursor()
        
        check_sql = """
            SELECT isPublicStatistics, account_id FROM Poll
            WHERE id = %s;
            """

        cursor.execute(check_sql, (poll_id,))
        poll = cursor.fetchone()

        if poll:
            print("poll_id: {}".format(poll[0]))
            print("user_id: {}".format(user_id))
            if poll[0] == False and poll[1] != user_id:
                raise UnauthorizedAccess()
            else:
                return True
        else:
            raise NoObjectFound()

        cursor.close()
        conn.close()
