from .connect_database import getConnection
from models.vo.poll import Poll
from models.vo.exceptions import NoObjectFound, UnauthorizedAccess, ExceededVotes
from models.dao.optionsDAO import OptionsDAO


class PollDAO:

    def create_poll(poll):
        conn = getConnection()
        cursor = conn.cursor()
        poll_sql = """
            INSERT INTO Poll (question, isclosed, ispublicstatistics, timeLimit, 
                            numchosenoptions, account_id, limit_vote_per_user) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """

        cursor.execute(poll_sql, (poll.question, poll.isClosed, poll.isPublicStatistics, 
            poll.timeLimit, poll.numChosenOptions, poll.account_id, poll.limit_vote_per_user))

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

        print(poll.account_id)
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
            poll_dic["options"] = OptionsDAO.getOptionsByPollId(current_poll[0])
            polls_array.append(poll_dic)
            current_poll = cursor.fetchone()

        cursor.close()
        conn.close()

        return polls_array

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
                poll_dic["options"] = OptionsDAO.getOptionsByPollId(current_poll[0])
                polls_array.append(poll_dic)
                current_poll = cursor.fetchone()

            cursor.close()
            conn.close()

            return polls_array
        else:
            raise NoObjectFound()


    def polls_result(poll_id, user_id):
        conn = getConnection()
        cursor = conn.cursor()
        
        check_sql = """
            SELECT isPublicStatistics, account_id FROM Poll
            WHERE id = %s;
            """

        cursor.execute(check_sql, (poll_id,))
        poll = cursor.fetchone()

        if poll:
            if poll[0] == False and poll[1] != user_id:
                raise UnauthorizedAccess()
            else:
                poll_sql = """
                    SELECT options.id, options.optiontext, COUNT(vote.id)
                    FROM vote
                    RIGHT JOIN options ON options.id = vote.option_id
                    WHERE options.poll_id = %s
                    GROUP BY options.id;
                    """

                cursor.execute(poll_sql, (poll_id,))
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
        conn.close()

        return {"options": options_array, "total": str(total)}