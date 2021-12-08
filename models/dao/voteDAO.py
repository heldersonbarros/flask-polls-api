from .connect_database import getConnection
from models.vo.vote import Vote
from models.vo.exceptions import ExceededVotes

class VoteDAO:

    def vote(vote):
        conn = getConnection()
        cursor = conn.cursor()

        check_sql = """
            SELECT poll.id FROM Poll WHERE id = %s
        """

        cursor.execute(check_sql, (vote.poll_id,))
        
        if (cursor.fetchone()):
            if (vote.account_id != 0):
                vote_sql = """
                        INSERT INTO vote (poll_id, option_id, account_id)
                        SELECT %s, %s, %s
                        FROM vote
                        JOIN poll ON vote.poll_id = poll.id
                        WHERE poll.id = %s AND poll.timeLimit > CURRENT_TIMESTAMP AND vote.account_id = %s
                        GROUP BY vote.account_id, poll.limit_vote_per_user
                        HAVING COUNT (*) < poll.limit_vote_per_user;
                        """

                cursor.execute(vote_sql, (vote.poll_id, vote.option_id, vote.account_id, vote.poll_id, vote.account_id))
                if (cursor.fetchone() == None):
                    raise ExceededVotes()
            else:
                vote_sql =  """
                INSERT INTO vote (poll_id, option_id)
                SELECT %s, %s
                FROM poll
                WHERE poll.id = %s AND (poll.timeLimit IS NULL OR poll.timeLimit > CURRENT_TIMESTAMP);
                """
            
            cursor.execute(vote_sql, (vote.poll_id, vote.option_id, vote.poll_id))
        else:
            raise NoObjectFound()

        conn.commit()
        cursor.close()
        conn.close()
