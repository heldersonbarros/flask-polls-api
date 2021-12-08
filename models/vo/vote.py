class Vote:
    def __init__(self, poll_id, option_id, account_id, id=None):
        self.id = id
        self.poll_id = poll_id
        self.option_id = option_id
        self.account_id = account_id