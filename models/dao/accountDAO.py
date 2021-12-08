from .connect_database import getConnection
from models.vo.account import Account
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

class AccountDAO:

    def verify_token(token, secret_key):
        data = jwt.decode(token, secret_key, algorithms=['HS256'])

        conn = getConnection()
        cursor = conn.cursor()
        account_sql = """
        SELECT * FROM ACCOUNT WHERE id = %s;
        """
        
        cursor.execute(account_sql, (data["id"],))
        current_user = cursor.fetchone()
        cursor.close()
        conn.close()

        return current_user[0]

    def create_account(account):
        conn = getConnection()
        cursor = conn.cursor()
        account_sql = """
            INSERT INTO Account (name, email, username, password) VALUES (%s, %s, %s, %s)
            """
        
        cursor.execute(account_sql, (account.name, account.email, account.username, account.password))
        conn.commit()
        cursor.close()
        conn.close()

    def login(username, password):
        conn = getConnection()
        cursor = conn.cursor()

        account_sql ="""
            SELECT * FROM Account WHERE username = %s
            """
        
        cursor.execute(account_sql, (username,))
        account = cursor.fetchone()

        if account:
            accountObject = Account(id=account[0], name=account[1], email=account[2], username=account[3], password=account[4])
            if accountObject.verify_password(password):
                return account[0]

        cursor.close()
        conn.close()

    def update_account(account):
        conn= getConnection()
        cursor = conn.cursor()
        
        account_sql = """
            UPDATE Account set name = %s, username = %s, email = %s
            WHERE id = %s;
            """

        cursor.execute(account_sql, (account.name, account.username, account.email, account.id))
        
        conn.commit()
        cursor.close()
        conn.close()

    def delete_account(id):
        conn = getConnection()
        cursor = conn.cursor()

        account_sql = """
            DELETE FROM Account WHERE id=%s
        """

        cursor.execute(account_sql, (id,))
        
        conn.commit()
        cursor.close()
        conn.close()