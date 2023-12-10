class Categories:
    categories = list()
    
    def __init__(self):
        """Initialize the class with a default category structure."""
        self.categories = ['expense', ['food', ['meal', 'snack', 'drink'], 'transportation', ['bus', 'railway']], 'income', ['salary', 'bonus', 'initial']]
    
    def view_categories(self, categories=None, dep=0):
        """Recursively display all categories and subcategories with increased indentation for each level."""
        if categories is None:
            categories = self.categories
        for i in categories:
            if isinstance(i, list):
                self.view_categories(i, dep + 1)
            else:
                print("  " * dep + "- " + i)
    
    def is_category_valid(self, category, categories=None):
        """Check if a given category exists in the category list."""
        if categories is None:
            categories = self.categories
        for i in categories:
            if isinstance(i, list):
                if self.is_category_valid(category, i):
                    return True
            else:
                if i == category:
                    return True
        return False
    
    def find_subcategories(self, category, categories=None):
        """Recursively find all subcategories of a given category using a generator."""
        if categories is None:
            categories = self.categories

        def find_subcategories_gen(category, categories, found = False):
            for i in range(len(categories)):
                if found and isinstance(categories[i], list) is False:
                    yield categories[i]
                elif categories[i] == category:
                    yield categories[i]
                    if i + 1 < len(categories) and isinstance(categories[i + 1], list):
                        yield from find_subcategories_gen(category, categories[i + 1], True)
                    break
                elif isinstance(categories[i], list):
                    yield from find_subcategories_gen(category, categories[i], found)

        return list(find_subcategories_gen(category, categories))


if __name__ == "__main__":
    categories = Categories()
    categories.view_categories()
    print(categories.find_subcategories('expense'))
    print(categories.find_subcategories('transportation'))
    print(categories.find_subcategories('salary'))
    print(categories.find_subcategories('null'))
