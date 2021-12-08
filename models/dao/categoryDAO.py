from .connect_database import getConnection
from models.vo.poll import Poll
from models.dao.optionsDAO import OptionsDAO
from models.vo.exceptions import NoObjectFound

class CategoryDAO:

    def category(category_name):
        conn = getConnection()
        cursor = conn.cursor()

        check_sql = "SELECT id FROM Category WHERE categoryname = %s"

        cursor.execute(check_sql,  (category_name,))
        poll_id = cursor.fetchone()

        if poll_id:
            poll_sql = """
                SELECT poll.*, 
                ARRAY_TO_STRING( ARRAY_AGG(Options.id|| ' ' || Options.optiontext), ',')
                FROM poll
                LEFT JOIN options ON poll.id = options.poll_id
                JOIN categorypoll ON poll.id = categorypoll.poll_id
                JOIN category ON category.id = categorypoll.category_id
                WHERE category.id = %s
                GROUP BY poll.id
                ORDER BY created_at DESC;
            """

            cursor.execute(poll_sql, (poll_id[0],))
            current_poll = cursor.fetchone()

            polls_array = []
            while current_poll is not None:
                poll_object = poll_object = Poll(id= current_poll[0], question= current_poll[1], isClosed= current_poll[2],
                            isPublicStatistics= current_poll[3], numChosenOptions= current_poll[4], 
                            timeLimit= current_poll[5], account_id= current_poll[6], created_at= current_poll[7], limit_vote_per_user= current_poll[0])

                options = current_poll[9].split(",")
                

                poll_dic = poll_object.get_json()
                poll_dic["options"]= OptionsDAO.getOptionsByPollId(current_poll[0])
                polls_array.append(poll_dic)
                current_poll = cursor.fetchone()


        else:
            raise NoObjectFound()

           
        cursor.close()
        conn.close()
        return polls_array


    def listAll():
        conn = getConnection()
        cursor = conn.cursor()
        account_sql = """
        SELECT * FROM Category
        """
        
        cursor.execute(account_sql)
        current_category = cursor.fetchone()

        category_array = []
        while current_category is not None:
            category_dic = {}
            category_dic["id"] = current_category[0]
            category_dic["name"] = current_category[1]
            category_array.append(category_dic)

            current_category = cursor.fetchone()

        cursor.close()
        conn.close()

        return category_array