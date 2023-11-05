import auth
from datetime import datetime

class App:
    account = None # Account object
    detailCollection = None # Collection of detail records
    userCollection = None # Collection of all user records
    record = None # All detail records of current user
    user = None # Current user
    
    def sync(self):
        # Update detailCollection, userCollection, record and user
        self.detailCollection = self.account.db[self.account.username]
        self.userCollection = self.account.db.users
        self.record = list(self.detailCollection.find(sort=[("time", 1), ("description", 1)]))
        self.user = self.userCollection.find_one({"username": self.account.username})
        
        # Update local database
        file = open(f"../database/{self.account.username}.txt", "r+")
        lines = file.readlines()
        file.close()
        
        localId = cloudId = 0
        cloudData = [
            f"{record.get('time')}, {record.get('description')}, {record.get('amount')}, {record.get('deleted')}"
            for record in self.record
        ]
        localData = lines[1:]
        cloudData.sort()
        localData.sort()
        
        print("Local Database: ", localData)
        print("Cloud Database: ", cloudData)
        
        if cloudData == localData:
            print("No need to update local database.")
        else:
            print("We found some version conflicts")        
            print("Local Database: ", localData)
            print("Cloud Database: ", cloudData)
            
            option = ""
            while (option != "local" and option != "cloud"):
                option = input("Which version do you want to keep? [local | cloud]\n")
            
            if option == "cloud": # TODO: 將雲端的資料（包含總額）下載到本地
                file = open(f"../database/{self.account.username}.txt", "w+")
                file.writelines(lines[0])
                file.writelines([f"{record.get('time')}, {record.get('description')}, {record.get('amount')}, {record.get('deleted')}\n" for record in self.record])
                file.close()
            else: # TODO: 將本地的資料（包含總額）上傳到雲端
                self.detailCollection.delete_many({})
                
                
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
                check = input("Are you sure to exit? [y | n]\n")
                if check == "y":
                    break
            else:
                print("Invalid operation, please input login, register or exit.")
                
        # sync local database and cloud database
        self.sync()
        return
    
    def add(self):
        # Parse input
        contents = list(map(str, input("Add some expense or income records with description and amount: \ndesc1 amt1, desc2 amt2, desc3 amt3, ...\n").split(sep=", ")))
        
        parts = list(list())
        # check input format is valid and 
        for content in contents:
            parts.append(content.rsplit(" ", 1))
            if len(parts[-1]) < 2:
                print("Invalid input!")
                return
            try:
                amount = int(parts[-1][1])
            except:
                print("Invalid input!")
                return        
        
        # ask user to check input is correct
        print("Here's your expense and income records: ")
        for content in contents:
            print(content)
        
        check = input("Do you want to continue? [Y/N]")
        
        if check != "Y":
            return
    
        for part in parts:
            description = part[0]
            amount = int(part[1])
            # Add record to database
            self.detailCollection.insert_one({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "description": description, "amount": amount, "deleted": False})
            # Update balance
            self.userCollection.update_one({"username": self.account.username}, {"$inc": {"balance": +amount}})
            # Update user
            self.user = self.userCollection.find_one({"username": self.account.username})
            # Update record
            self.record = list(self.detailCollection.find())
            
        print("Add successfully! Now you have:", self.user["balance"], "dollars.")
    
    def balance(self):
        print("You have", self.user["balance"], "dollars.")
        
    def list(self):
        for (index, record) in enumerate(self.record):
            print(f"{index}) ", end="")
            output = f"{record.get('time')}: {record.get('description')} ({record.get('amount')})"
            if record.get("deleted") == True:
                for i in output:
                    print("\u0336" + i, end="")
                print("")
            else:
                print(f"{record.get('time')}: {record.get('description')} ({record.get('amount')})")
            
    def delete(self):
        index = int(input("Please enter the index of the record you want to delete: "))
        
        print(self.record[index].get("amount"))
        # Review balance
        self.userCollection.update_one({"username": self.account.username}, {"$inc": {"balance": -int(self.record[index].get("amount"))}})
        # Update user
        self.user = self.userCollection.find_one({"username": self.account.username})
        # Delete record
        self.detailCollection.update_one({"_id": self.record[index].get("_id")}, {"$set": {"deleted": True}})
        # Update record list
        self.record = list(self.detailCollection.find(sort=[("time", 1), ("description", 1)]))
            
    def user_mode(self):
        operation = ""
        while operation != "logout":
            operation = input("Please enter your operation: [logout | add | balance | view | delete | exit]\n")
            
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
                self.list()
            elif operation == "exit":
                check = input("Are you sure to exit? [y | n]\n")
                if check == "y":
                    break
            else:
                print("Invalid operation, please input logout, add, balance, list, delete or exit.")        
        return

if __name__ == "__main__":
    output = "test"
    print("1) ", end="")
    output.join("\u0336")
    print(output)
    # for i in output:
    #     print("\u0336" + i, end="")
    # print("\n")
    
    # App = App()
    # App.add()