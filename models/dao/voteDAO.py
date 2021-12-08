from .connect_database import getConnection
from models.vo.vote import Vote
from models.vo.exceptions import ExceededVotes, NoObjectFound, UnauthorizedAccess

class VoteDAO:

    def vote(vote):
        conn = getConnection()
        cursor = conn.cursor()

        check_sql = """
            SELECT poll.limit_vote_per_user, poll.id FROM Poll 
            JOIN Options on poll.id = options.poll_id
            WHERE poll.id = %s AND options.id = %s AND
            (timeLimit > CURRENT_TIMESTAMP OR timeLimit IS NULL) AND
            isClosed = false;
        """

        cursor.execute(check_sql, (vote.poll_id, vote.option_id))

        check_result = cursor.fetchone()

        if check_result:
            if (check_result[0]!=0):
                if (vote.account_id != 0):
                    vote_sql = """
                            INSERT INTO vote (poll_id, option_id, account_id) 
                            SELECT %s, %s, %s
                            FROM vote
                            JOIN poll ON vote.poll_id = poll.id
                            WHERE poll.id = %s AND vote.account_id = %s
                            HAVING COUNT (*) < %s OR %s = 0
                            RETURNING id;
                            """

                    cursor.execute(vote_sql, (vote.poll_id, vote.option_id, vote.account_id, vote.poll_id, vote.account_id, check_result[0], check_result[0]))
                    conn.commit()

                    if (cursor.fetchone()==None):
                        raise ExceededVotes()
                else:
                    raise UnauthorizedAccess()
            else:
                if (vote.account_id != 0):
                    vote_sql =  """
                    INSERT INTO vote (poll_id, option_id, account_id)
                    SELECT %s, %s, %s
                    FROM poll
                    WHERE poll.id = %s
                    """

                    cursor.execute(vote_sql, (vote.poll_id, vote.option_id, vote.account_id, vote.poll_id))
                else:
                    vote_sql =  """
                    INSERT INTO vote (poll_id, option_id)
                    SELECT %s, %s
                    FROM poll
                    WHERE poll.id = %s
                    """
                    cursor.execute(vote_sql, (vote.poll_id, vote.option_id, vote.poll_id))
                
                conn.commit()
        else:
            raise NoObjectFound()


        cursor.close()
        conn.close()
