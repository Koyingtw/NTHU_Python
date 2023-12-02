import auth
import category as cate
from datetime import datetime
import difflib

# TODO: Change classname to Record (done)
class Record:
    account = None # Account object
    detailCollection = None # Collection of detail records
    userCollection = None # Collection of all user records
    record = None # All detail records of current user
    user = None # Current user
    localBalance = None # Balance of local database
    Categories = None # Category class
    
    # TODO: add categories to data format (done)
    
    # local data format: 
    # first line: balance
    # other lines: time, category, description, amount, deleted
    
    # cloud data format:
    # 0: time, 1: category, 2: description, 3: amount, 4: deleted
    
    def record_key(self, record): # sort by time and description # TODO: add categories record (done)
        parts = record.split(', ')
        record_time = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
        record_description = parts[2]
        return (record_time, record_description)
    
    def overwrite_local(self): # TODO: add categories record (done)
        file = open(f"../database/{self.account.username}.txt", "w+")
        file.writelines(f"{self.user['balance']}\n")
        file.writelines([f"{record.get('time')}, {record.get('category')}, {record.get('description')}, {record.get('amount')}, {record.get('deleted')}\n" for record in self.record])
        file.close()
        self.localBalance = self.user["balance"]
        
    def overwrite_cloud(self, lines): # TODO: add categories record (done)
        self.detailCollection.delete_many({})
        amount = int(lines[0])
        
        # Update balance
        self.userCollection.update_one({"username": self.account.username}, {"$set": {"balance": amount}})
        # Update record
        for i in range(1, len(lines)):
            parts = lines[i].split(sep=", ")
            self.detailCollection.insert_one({"time": parts[0], "category": parts[1], "description": parts[2], "amount": int(parts[3]), "deleted": parts[4]})
        # Update record list
        self.record = list(self.detailCollection.find(sort=[("time", 1), ("description", 1)]))
        
    def validate_local(self): # TODO: add categories record (done)
        # Read local database into lines
        with open(f"../database/{self.account.username}.txt", "r") as file:
            lines = [line.strip() for line in file]
        try:
            amount = int(lines[0])
        except:
            return False
        
        for i in range(1, len(lines)):
            parts = lines[i].split(sep=", ")
            if len(parts) != 5:
                return False
            try:
                datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
            except:
                return False
            try:
                int(parts[3])
            except:
                return False
            if parts[4] != "True" and parts[4] != "False":
                return False
    
    def sync(self): # TODO: add categories record (done)
        cloudData = []
        if self.account.connected == True:
            # Update detailCollection, userCollection, record and user
            self.detailCollection = self.account.db[self.account.username]
            self.userCollection = self.account.db.users
            self.record = list(self.detailCollection.find(sort=[("time", 1), ("description", 1)]))
            self.user = self.userCollection.find_one({"username": self.account.username})
            cloudData.append(str(self.user["balance"]))
            cloudData.extend([f"{record.get('time')}, {record.get('category')}, {record.get('description')}, {record.get('amount')}, {record.get('deleted')}" for record in self.record])
            
        
        if self.validate_local() == False:
            if self.account.connected == False:
                print("Format of local database is invalid! Please connect to the Internet and try again.")
                exit(0)
            else:
                print("Format of local database is invalid! We will update local database with cloud database.")
                self.overwrite_local()
            return
        elif self.account.connected == False:
            print("Format of local database is valid! But you are not connected to the Internet, so we will not compare local database and cloud database.")
            return
        else:
            print("Format of local database is valid! We will compare local database and cloud database.")
            
        # Read local database into lines
        with open(f"../database/{self.account.username}.txt", "r") as file:
            lines = [line.strip() for line in file] # Read all lines and ignore the last \n
            
        localId = cloudId = 0
        localData = lines
        self.localBalance = int(lines[0])
        
        # sort by time and description from second line
        localData[1:] = sorted(localData[1:], key=self.record_key)
        
        
        print("Local Database: ", localData)
        print("Cloud Database: ", cloudData)
        

        if cloudData == localData:
            print("No need to update local database.")
        else:
            print("We found some version conflicts")       
            
            differ = difflib.Differ()
            diff = differ.compare(localData, cloudData)
            print("\n".join(diff)) 
            
            option = ""
            while (option != "local" and option != "cloud"):
                option = input("Which version do you want to keep? [local | cloud]\n")
            
            if option == "cloud": 
                self.overwrite_local()
            else: 
                self.overwrite_cloud(lines)
        
        return
    
    def guest_mode(self): 
        self.account = auth.Account() # Create an Account object
        
        while (self.account.status == "logout"):
            operation = input("Please enter your operation: [login | register | exit]\n")
            
            if operation == "login":
                self.account.login()
            elif operation == "register":
                self.account.register()
            elif operation == "exit":
                check = input("Are you sure to exit? [y|n]\n")
                if check == "y":
                    exit(0)
            else:
                print("Invalid operation, please input login, register or exit.")
                
        # sync local database and cloud database
        self.sync()
        return
    
    def add(self): # TODO: add categories record (done)
        # Parse input
        contents = list(map(str, input("Add some expense or income records with description and amount: \ncate1 desc1 amt1, cate2 desc2 amt2, cate3 desc3 amt3, ...\n").split(sep=", ")))
        
        parts = list(list())
        # check input format is valid and 
        for content in contents:
            parts.append(content.rsplit(" ", 1))
            category = ""
            amount = 0
            if len(parts[-1]) < 2:
                print("Invalid input!")
                return
            else:
                # TODO: check categories are valid (done)
                category = parts[-1][0].split(sep=" ")[0]
                if self.Categories.is_category_valid(category) == False:
                    print("Invalid category!\nThe specified category is not in the category list.\nYou can check the category list by command \"view categories\".\nFail to add a record.")
                    return        
            try:
                amount = int(parts[-1][1])
                
            except:
                print("Invalid input!")
                return        
            
            # Check amount is valid (expense: negative, income: positive)
            if amount < 0 and self.Categories.find_subcategories("expense").count(category) == 0:
                print("Invalid amount!\nThe amount of income should be negative.\nFail to add a record.")
                return
            elif amount > 0 and self.Categories.find_subcategories("income").count(category) == 0:
                print("Invalid amount!\nThe amount of expense should be positive.\nFail to add a record.")
                return
            
        
        # ask user to check input is correct
        print("Here's your expense and income records: ")
        for content in contents:
            print(content)
        
        check = input("Do you want to continue? [Y/N]")
        
        if check != "Y":
            return

        amountSum = sum(int(part[1]) for part in parts)
        lines = []
        with open(f"../database/{self.account.username}.txt", "r") as file:
            lines = [line.strip() + "\n" for line in file]
            
        
        for part in parts: 
            category = part[0].split(sep=" ")[0]
            description = part[0].split(sep=" ", maxsplit=1)[1]
            amount = int(part[1])
            
            # Update local database buffer
            lines.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, {category}, {description}, {amount}, False\n")
            
            if self.account.connected == True:
                # Add record to database
                self.detailCollection.insert_one({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "category": category, "description": description, "amount": amount, "deleted": False})
                # Update record
                self.record = list(self.detailCollection.find())
            
        # Update changes in buffer to local database
        lines[0] = str(int(lines[0].strip()) + amountSum) + "\n"
        self.localBalance = int(lines[0].strip())
        with open (f"../database/{self.account.username}.txt", "w") as file:
            for line in lines:
                file.writelines(line)
        
        
        if self.account.connected == True:
            # Update balance
            self.userCollection.update_one({"username": self.account.username}, {"$inc": {"balance": +amountSum}})
            # Update user
            self.user = self.userCollection.find_one({"username": self.account.username})
            
        
        print("Add successfully! Now you have:", self.user["balance"], "dollars.")
    
    def balance(self):
        print("You have", self.localBalance, "dollars.")
        
    def list(self, all, target_categories = None): # TODO: add categories record (done)
        self.balance()
        with open(f"../database/{self.account.username}.txt", "r") as file:
            lines = [line.strip() for line in file]
        for (index, record) in enumerate(lines[1:]):
            record = record.split(sep=", ")
            
            # TODO: add categories filter (done)
            if target_categories is not None and record[1] not in target_categories:
                continue
            
            if record[4] == "True" and all == False:
                continue
            
            print(f"{index}) ", end="")
            output = f"{record[0]}: {record[1]} | {record[2]} ({record[3]})"
            if record[4] == "True":
                for i in output:
                    print("\u0336" + i, end="")
                print("")
            else:
                print(output)
            
    def delete(self): # TODO: add categories record (done)
        index = int(input("Please enter the index of the record you want to delete: "))
        
        # Update local database buffer
        with open(f"../database/{self.account.username}.txt", "r") as file:
            lines = [line.strip() + "\n" for line in file]
        targetLine = list(map(str, lines[index + 1].split(sep=", ")))
        targetLine[4] = "True"
        lines[index + 1] = ", ".join(targetLine) + "\n"
        self.localBalance -= int(targetLine[3])
        lines[0] = str(self.localBalance) + "\n"
        
        # Update changes in buffer to local database
        with open (f"../database/{self.account.username}.txt", "w") as file:
            for line in lines:
                file.writelines(line)
        
        if self.account.connected == True:    
            # Review balance
            self.userCollection.update_one({"username": self.account.username}, {"$inc": {"balance": -int(self.record[index].get("amount"))}})
            # Update user
            self.user = self.userCollection.find_one({"username": self.account.username})
            # Delete record
            self.detailCollection.update_one({"_id": self.record[index].get("_id")}, {"$set": {"deleted": True}})
            # Update record list
            self.record = list(self.detailCollection.find(sort=[("time", 1), ("description", 1)]))
            
        print("Delete successfully! Now you have:", self.localBalance, "dollars.")
    
    def find(self): # TODO: user can find records by category (done)
        category = input("Which category do you want to find? ")
        if self.Categories.is_category_valid(category) == False:
            print("Invalid category!\nThe specified category is not in the category list.\nYou can check the category list by command \"view categories\".\nFail to find a record.")
            return
    
        subcategories = self.Categories.find_subcategories(category)
        self.list(False, subcategories)
        
            
    def user_mode(self):
        operation = ""
        # TODO: Call initialize_categories before the while loop and assign the returned value to a variable categories. (done)
        self.Categories = cate.Categories()

        while operation != "logout":
            operation = input("Please enter your operation: [logout | add | balance | view | view all | delete | view categories | find | exit]\n")
            
            if operation == "logout":
                self.account.logout()
                break
            elif operation == "add":
                self.add()
            elif operation == "balance":
                self.balance()
            elif operation == "delete":
                self.delete()
            elif operation == "view":
                self.list(False)
            elif operation == "view all":
                self.list(True)
            elif operation == "exit":
                check = input("Are you sure to exit? [y|n]\n")
                if check == "y":
                    exit(0)
            # TODO: Add the elif branch for view categories. (done)
            elif operation == "view categories":
                self.Categories.view_categories()
            # TODO: Add the elif branch for find. (done)
            elif operation == "find":
                self.find()
            else:
                print("Invalid operation, please input logout, add, balance, list, delete or exit.")        
        return

if __name__ == "__main__":
    output = "test"
    print("1) ", end="")
    output.join("\u0336")
    print(output)