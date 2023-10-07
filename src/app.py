import auth
from datetime import datetime

class App:
    account = None # Account object
    detailCollection = None # Collection of detail records
    userCollection = None # Collection of all user records
    record = None # All detail records of current user
    user = None # Current user
    
    def guest_mode(self):
        self.account = auth.Account()
        
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
        
        # Update detailCollection, userCollection, record and user
        self.detailCollection = self.account.db[self.account.username]
        self.userCollection = self.account.db.users
        self.record = list(self.detailCollection.find())
        self.user = self.userCollection.find_one({"username": self.account.username})
        return
    
    def add(self):
        # Parse input
        content = input("Add an expense or income record with description and amount: ")
        parts = content.rsplit(" ", 1)
        if len(parts) < 2:
            print("Invalid input!")
            return
        description = parts[0]
        try:
            amount = int(parts[1])
        except:
            print("Invalid input!")
            return        
        
        # Add record to database
        self.detailCollection.insert_one({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "description": description, "amount": amount})
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
            print(f"{index}) {record.get('time')}: {record.get('description')} ({record.get('amount')})")
            
    def delete(self):
        index = int(input("Please enter the index of the record you want to delete: "))
        
        print(self.record[index].get("amount"))
        # Review balance
        self.userCollection.update_one({"username": self.account.username}, {"$inc": {"balance": -int(self.record[index].get("amount"))}})
        # Update user
        self.user = self.userCollection.find_one({"username": self.account.username})
        # Delete record
        self.detailCollection.delete_one(self.record[index])
        # Update record list
        self.record = list(self.detailCollection.find())
            
    def user_mode(self):
        operation = ""
        while operation != "logout":
            operation = input("Please enter your operation: [logout | add | balance | list | delete | exit]\n")
            
            if operation == "logout":
                self.account.logout()
                break
            elif operation == "add":
                self.add()
            elif operation == "balance":
                self.balance()
            elif operation == "delete":
                self.delete()
            elif operation == "list":
                self.list()
            elif operation == "exit":
                check = input("Are you sure to exit? [y | n]\n")
                if check == "y":
                    break
            else:
                print("Invalid operation, please input logout, add, balance, list, delete or exit.")        
        return
