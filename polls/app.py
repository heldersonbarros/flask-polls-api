from flask import Flask
from modules.account import account
from modules.category import category
from modules.poll import poll
from modules.vote import vote

app = Flask(__name__)

app.config['SECRET_KEY'] = "9u=brky[E?^MCVWZ7mtZj]PB?;|iP`"

app.register_blueprint(account)
app.register_blueprint(category)
app.register_blueprint(poll)
app.register_blueprint(vote)

if __name__ == '__main__':
    app.run(debug= True)