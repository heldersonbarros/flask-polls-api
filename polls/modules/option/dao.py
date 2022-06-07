from utils.connect_database import getConnection
from modules.option.model import Options

class OptionsDAO:

    def create_option(option):
        conn = getConnection()
        cursor = conn.cursor()

        options_sql = """
            INSERT INTO Options (optiontext, poll_id) 
            VALUES (%s, %s)
            """

        cursor.execute(options_sql, (option.OptionText, option.poll_id))
        conn.commit()
        cursor.close()
        conn.close()

    def getOptionsByPollId(id):
        conn = getConnection()
        cursor = conn.cursor()
        query = """
            SELECT * FROM Options WHERE poll_id = %s
        """
        cursor.execute(query, (id,))

        current_option = cursor.fetchone()
        options_array = []

        while current_option is not None:
            option_object = Options(id=current_option[0], OptionText=current_option[1], poll_id=current_option[2])
            option_dic = option_object.get_json()
            options_array.append(option_dic)

            current_option = cursor.fetchone()

        cursor.close()
        conn.close()

        return options_array

    def getOptionsVotesResult(poll_id):
        conn = getConnection()
        cursor = conn.cursor()

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
        
        
        cursor.close()
        conn.close()

        return {"options": options_array, "total": str(total)}