"""
class Poll:
    def __init__(self):
        self.json = {} 
        self.columns = ["question", "isClosed", "isPublicStatistics", "numChosenOptions", "timeLimit",
                "account_id", "created_at"]

    def from_array(self, array):
        all_columns = ["id", "question", "isClosed", "isPublicStatistics", "numChosenOptions", "timeLimit",
            "account_id", "created_at"]
        for i in range(len(array)):
            self.json[all_columns[i]] = array[i]

    def from_dic(self, dic):
        for column in self.columns:
            self.json[column] = dic[column]

    def get_json(self):
        return self.json
"""

class Poll:
    def __init__(self, isClosed, isPublicStatistics, timeLimit, account_id, limit_vote_per_user,
                question=None, numChosenOptions=None, created_at=None, id=None):
        self.id = id
        self.question = question
        self.isClosed = isClosed
        self.isPublicStatistics = isPublicStatistics
        self.numChosenOptions = numChosenOptions
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
            "numChosenOptions": self.numChosenOptions,
            "timeLimit": self.timeLimit,
            "account_id": self.account_id,
            "created_at": self.created_at,
            "limit_vote_per_user": self.limit_vote_per_user
        }