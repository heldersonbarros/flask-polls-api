class Category():
    def __init__(self, id, categoryName):
        self.id = self.id
        self.categoryName = self.categoryName

    def get_json(self):
        return dic(
            id = self.id,
            categoryName = self.categoryName
            )