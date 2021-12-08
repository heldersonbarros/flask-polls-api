from .connect_database import getConnection
from models.vo.options import Options

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

