import app

if __name__ == "__main__":
    print("Welcome to Pymoney!")
    while True:
        pymoney = app.Record() # Create an App object
        pymoney.guest_mode() # Guest mode (hasn't logged in yet)
        pymoney.user_mode() # User mode (has logged in)
    