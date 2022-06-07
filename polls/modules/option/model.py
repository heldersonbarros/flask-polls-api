class Options():
    def __init__(self, OptionText, poll_id, id=None):
        self.id = id
        self.OptionText = OptionText
        self.poll_id = poll_id

    def get_json(self):
        return {
            "id": self.id,
            "OptionText": self.OptionText,
            "poll_id": self.poll_id
        }