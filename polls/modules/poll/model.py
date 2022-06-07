class Poll:
    def __init__(self, isClosed, isPublicStatistics, account_id, timeLimit=None, limit_vote_per_user=None,
                question=None, created_at=None, id=None):
        self.id = id
        self.question = question
        self.isClosed = isClosed
        self.isPublicStatistics = isPublicStatistics
        self.timeLimit = timeLimit
        self.account_id = account_id
        self.created_at = created_at
        self.limit_vote_per_user = limit_vote_per_user

    def get_json(self):
        return {
            "id": self.id,
            "question": self.question,
            "isClosed": self.isClosed,
            "isPublicStatistics": self.isPublicStatistics,
            "timeLimit": self.timeLimit,
            "account_id": self.account_id,
            "created_at": self.created_at,
            "limit_vote_per_user": self.limit_vote_per_user
        }