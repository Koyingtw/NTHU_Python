# TODO: add category class (done)

class Categories:
    categories = list()
    
    def __init__(self):
        # TODO: initialize categories (done)
        self.categories = ['expense', ['food', ['meal', 'snack', 'drink'], 'transportation', ['bus', 'railway']], 'income', ['salary', 'bonus', 'initial']]
    
    def view_categories(self, categories = None, dep = 0):
        if categories is None:
            categories = self.categories
        # TODO: handle the base case and recursive case (done)
        for i in categories:
            if isinstance(i, list):
                self.view_categories(i, dep + 1)
            else:
                print("  " * dep + "- " + i)
        pass
    
    def is_category_valid(self, category, categories = None):
        if categories is None:
            categories = self.categories
        # TODO: returns True if category is in categories and False otherwise. (done)
        
        for i in categories:
            if isinstance(i, list):
                if self.is_category_valid(category, i):
                    return True
            else:
                if i == category:
                    return True
        return False
    
    def find_subcategories(self, category, categories=None):
        if categories is None:
            categories = self.categories

        def find_subcategories_gen(category, categories):
            for i in range(len(categories)):
                if categories[i] == category:
                    yield categories[i]
                    if i + 1 < len(categories) and isinstance(categories[i + 1], list):
                        yield from find_subcategories_gen(category, categories[i + 1])
                    break
                elif isinstance(categories[i], list):
                    yield from find_subcategories_gen(category, categories[i])

        return list(find_subcategories_gen(category, categories))

        
if __name__ == "__main__":
    categories = Categories()
    categories.view_categories()
    print(categories.find_subcategories('expense'))
    print(categories.find_subcategories('transportation'))
    print(categories.find_subcategories('salary'))
    print(categories.find_subcategories('null'))