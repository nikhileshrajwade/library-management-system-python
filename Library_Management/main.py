import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# +++++ LOAD DATA +++++
library = pd.read_excel("library_books.xlsx")
user = pd.read_excel("User_data.xlsx")
admin = pd.read_excel("Admin_data.xlsx")
removed_user = pd.read_excel("removed_user.xlsx")

# +++++ SAVE FUNCTIONS +++++
def save_user():
    user.to_excel("User_data.xlsx", index=False)

def save_library():
    library.to_excel("library_books.xlsx", index=False)

def save_removed_user():
    removed_user.to_excel("removed_user.xlsx", index=False)


# +++++ GLOBAL VARIABLES +++++
def save_data():
    global Book_ID, Book_Name_All, U_ID_All, U_Pass_All, A_ID_All, A_Pass_All, User_ID, attempt, ex_user
    Book_ID = np.array(library["Book_ID"]).astype(int)
    Book_Name_All = library["Book_Name"].astype(str).values
    U_ID_All = np.array(user["User_ID"]).astype(int)
    U_Pass_All = np.array(user["User_Pass"])
    A_ID_All = np.array(admin["Admin_ID"]).astype(int)
    A_Pass_All = np.array(admin["Admin_Pass"])
    ex_user = removed_user["User_ID"].dropna().astype(int).values


#---- No change needed variables ----
User_ID = None

#---- Total attempt for login ---- 
user_attempt = 3
admin_attempt = 3




# +++++ USER FINE +++++
def user_fine():
    user["Issue_Date_1"] = pd.to_datetime(user["Issue_Date_1"], dayfirst=True).dt.normalize()
    user["Issue_Date_2"] = pd.to_datetime(user["Issue_Date_2"], dayfirst=True).dt.normalize()
    user["Issue_Date_3"] = pd.to_datetime(user["Issue_Date_3"], dayfirst=True).dt.normalize()

    today = pd.Timestamp.today().normalize()

    g1 = np.where(user["Issue_Date_1"].isna(), 0, (today - user["Issue_Date_1"]).dt.days)
    g2 = np.where(user["Issue_Date_2"].isna(), 0, (today - user["Issue_Date_2"]).dt.days)
    g3 = np.where(user["Issue_Date_3"].isna(), 0, (today - user["Issue_Date_3"]).dt.days)

    fine = (
        np.where(g1 > 14, (g1 - 14) * 2, 0) +
        np.where(g2 > 14, (g2 - 14) * 2, 0) +
        np.where(g3 > 14, (g3 - 14) * 2, 0)
    )

    user["Fine"] = fine.astype(int)
    save_user()

def user_overdue():
    global ex_user, removed_user, U_ID_All, U_Pass_All
    user_fine()
    temp = user[user["Fine"]>500]["User_ID"].values
    user.drop(user[user["User_ID"].isin(temp)].index, inplace=True)
    ex_user = np.unique(np.append(ex_user, temp))
    new_df = pd.DataFrame({"User_ID": temp})
    removed_user = pd.concat([removed_user, new_df], ignore_index=True)
    removed_user.drop_duplicates(inplace=True)
    save_data()
    save_user()
    save_removed_user()
    
def show_data_user():
    books, days, fines = [], [], []
    today = pd.Timestamp.today().normalize()

    for i in range(3):
        bn = f"Book_Name_{i+1}"
        bd = f"Issue_Date_{i+1}"
        if not pd.isna(user.loc[user_index, bn]):
            d = (today - user.loc[user_index, bd]).days
            books.append(user.loc[user_index, bn])
            days.append(d)
            fines.append((d - 14) * 2 if d > 14 else 0)

    if len(books) > 0:
        plt.figure(figsize=(15,5))
        plt.bar(books, days)
        plt.title("Books vs Days Issued")
        plt.show()

        plt.figure(figsize=(15,5))
        plt.bar(books, fines)
        plt.title("Books vs Fine")
        plt.show()
    else:
        print("No books issued")

def book_issue():
    b_ID = input("""If want to Issue Book by name then press enter.
        Else enter the Book_ID:  """)
    if b_ID=="":
        book_name = input("Enter book name: (You can enter related word)--: ")
        sim_book=np.array([])
        sim_index=np.array([])
        n = 0
        for i in range(len(Book_Name_All)):
            if book_name.lower() in Book_Name_All[i].lower():
                sim_book= np.append(sim_book, Book_Name_All[i])
                sim_index = np.append(sim_index, i)
                n = n+1
                print(f"{n}. {Book_Name_All[i]}")
        
        if len(sim_book)==0:
            print("--Book not found--")
        else:
            temp_index= int(input("Enter the serial number: "))
            if temp_index < 1 or temp_index > len(sim_index):
                print("Invalid selection")
                return
            b_index = int(sim_index[temp_index-1])
            b_ID = Book_ID[b_index]
            
            if library.loc[b_index, "Copies"] == 0:
                print("Book out of stock")
                return
    else:
        b_ID = int(b_ID)
        if b_ID in Book_ID:
            idx = np.where(Book_ID == b_ID)[0]
            b_index = idx[0]
            if library.loc[b_index, "Copies"] == 0:
                print("Book out of stock")
                return
        else:
            print("Book not found")
            return
    for i in range(3):
        bn = f"Book_Name_{i+1}"
        bid = f"Book_ID_{i+1}"
        bd = f"Issue_Date_{i+1}"
        if pd.isna(user.loc[user_index, bn]):
            user.loc[user_index, bn] = Book_Name_All[b_index]
            user.loc[user_index, bid] = b_ID
            user.loc[user_index, bd] = pd.Timestamp.today().normalize()
            library.loc[b_index, "Copies"] -= 1
            if library.loc[b_index, "Copies"] == 0:
                library.loc[b_index, "Status"] = "Issued"
            print("--- Book Issued ---")
            save_data()
            save_user()
            save_library()
            return
    print("!!! Maximum Limit Reached !!!")

def book_reissue():
    b_ID = input("""If want to Re-Issue Book by name then press enter.
        Else enter the Book_ID:  """)
    if b_ID=="":
        book_name = input("Enter book name: (You can enter related word)--: ")
        sim_book=np.array([])
        sim_index=np.array([])
        cnt=0
        n=0
        for i in range(len(Book_Name_All)):
            if book_name.lower() in Book_Name_All[i].lower():
                sim_book= np.append(sim_book, Book_Name_All[i])
                sim_index = np.append(sim_index, i)
                n = n+1
                print(f"{n}. {Book_Name_All[i]}")
        
        if len(sim_book)==0:
            print("--Book not found--")
        else:
            temp_index= int(input("Enter the serial number: "))
            if temp_index < 1 or temp_index > len(sim_index):
                print("Invalid selection")
                return
            b_name = sim_book[temp_index-1]
    else:
        b_ID = int(b_ID)
        if b_ID in Book_ID:
            idx = np.where(Book_ID == b_ID)[0]
            b_index = idx[0]
            b_name = library.loc[b_index,"Book_Name"]  
        else:
            print("--- Book not found ---")
        for i in range(3):
            str_name = f"Book_Name_{i+1}"
            str_date = f"Issue_Date_{i+1}"
            if (b_name==user.loc[user_index, str_name]):
                user.loc[user_index, str_date] = pd.Timestamp.today().normalize()
                print("--- Book Re-Issued ---")
                save_data()
                save_user()
                return
        print("---Book Not Issued.---")

def book_return():
    b_ID = input("""If want to Return Book by name then press enter.
        Else enter the Book_ID:  """)
    if b_ID=="":
        book_name = input("Enter book name: (You can enter related word)--: ")
        sim_book=np.array([])
        sim_index=np.array([])
        n=0
        for i in range(len(Book_Name_All)):
            if book_name.lower() in Book_Name_All[i].lower():
                sim_book= np.append(sim_book, Book_Name_All[i])
                sim_index = np.append(sim_index, i)
                n = n+1
                print(f"{n}. {Book_Name_All[i]}")
        
        if len(sim_book)==0:
            print("--Book not found--")
        else:
            temp_index= int(input("Enter the serial number: "))
            if temp_index < 1 or temp_index > len(sim_index):
                print("Invalid selection")
                return
            b_index = int(sim_index[temp_index-1])
            b_ID = Book_ID[b_index]

    else:
        b_ID = int(b_ID)
        if b_ID in Book_ID:
            idx = np.where(Book_ID == b_ID)[0]
            b_index = idx[0]
        else:
            print("--- Book not found ---")
    for i in range(3):
        bn = f"Book_Name_{i+1}"
        bid = f"Book_ID_{i+1}"
        bd = f"Issue_Date_{i+1}"
        if user.loc[user_index, bid] == b_ID:
            user.loc[user_index, bn] = pd.NA
            user.loc[user_index, bid] = pd.NA
            user.loc[user_index, bd] = pd.NaT
            library.loc[b_index, "Copies"] += 1
            library.loc[b_index, "Status"] = "Available"
            print("--- Book Returned ---")
            save_data()
            save_user()
            save_library()
            return
    print("--- Book Not Issued ---")

# +++++ USER +++++
def login_user():
    global user_index 
    user_index = np.where(U_ID_All == User_ID)[0][0]

    while True:
        try:
            task = int(input('''Enter your choice:
    
    1. Show my data visually
    2. Issue a book
    3. Reissue a book
    4. Return a book
    5. Check fine
    6. Exit
    
    Enter choice: '''))
    
        # +++++ TASK 1 - USER VISUAL DATA +++++
            if task == 1:
                show_data_user()
        
            # +++++ TASK 2 - ISSUE BOOK +++++
            elif task == 2:
               book_issue()
        
            # +++++ TASK 3 - REISSUE BOOK +++++
            elif task == 3:
                book_reissue()
                    
        
            # +++++ TASK 4 - RETURN BOOK +++++
            elif task == 4:
                book_return()
                
        
            # +++++ TASK 5 - CHECK FINE +++++
            elif task == 5:
                user_fine()
                print("Total Fine ₹", user.loc[user_index, "Fine"])
                if user.loc[user_index, "Fine"] >= 250:
                    print("\033[31m!!! WARNING !!!\033[0m")
                    print("YOUR ACCOUNT MAY BE SUSPENDED IF FINE REACHES ₹500. PAY IT 'ASAP")
            
            # +++++ TASK 6 - EXIT +++++
            elif task == 6:
                print("---- THANK YOU ----")
                break
            
            else:
                print("!!! INVALID ENTRY !!!")
    
        except ValueError:
            print("!!! INVALID ENTRY !!!")


def create_user():
    global user
    uid = int(input("User ID: "))
    if uid in U_ID_All:
        print("!!! User already exists !!!")
    else:
        pwd = int(input("Password: "))
        row = {
        "User_ID": uid,
        "User_Pass": pwd,
        "Book_Name_1": pd.NA, "Book_ID_1": pd.NA, "Issue_Date_1": pd.NaT,
        "Book_Name_2": pd.NA, "Book_ID_2": pd.NA, "Issue_Date_2": pd.NaT,
        "Book_Name_3": pd.NA, "Book_ID_3": pd.NA, "Issue_Date_3": pd.NaT,
        "Fine": 0
        }
        user = pd.concat([user, pd.DataFrame([row])], ignore_index=True)
        print("--- USER CREATED SUCCESSFULLY ---")
        save_data()
        save_user()
    return login_admin()

def delete_user():
    global user
    uid = int(input("User ID to delete: "))
    if uid in U_ID_All:
        user.drop(user[user["User_ID"] == uid].index, inplace=True)
        print("--- USER DELETED SUCCESSFULLY ---")
        save_data()
        save_user()
    else:
        print("--- User Not Found ---")
    return login_admin()

def book_insert():
    global library
    bid = int(input("Book ID: "))
    copies = int(input("Copies to add: "))
    if bid in Book_ID:
        idx = np.where(Book_ID == bid)[0][0]
        library.loc[idx, "Copies"] += copies
        library.loc[idx, "Status"] = "Available"
        print("--- STOCK UPDATED SUCCESSFULLY ---")
    else:
        name = input("Book Name: ")
        price = int(input("Price: "))
        row = {
            "Book_ID": bid,
            "Book_Name": name,
            "Price": price,
            "Copies": copies,
            "Status": "Available"
        }
        library = pd.concat([library, pd.DataFrame([row])], ignore_index=True)
        print("--- NEW BOOK ADDED SUCCESSFULLY ---")
    save_data()
    save_library()
    Book_ID = np.array(library["Book_ID"])
    return login_admin()

def book_delete():
    global library
    bid = int(input("Book ID to delete: "))
    if bid in Book_ID: 
        library.drop(library[library["Book_ID"] == bid].index, inplace=True)
        print("--- STOCK UPDATED SUCCESSFULLY ---")
        save_data()
        save_library()
    else:
        print("--- Book Not Found ---")
    return login_admin()

def lib_status():
    total = len(library)
    avail = (library["Status"] == "Available").sum()
    issued = total - avail
    fine = user["Fine"].sum()
    temp = user[user["Fine"]>500]["User_ID"].values
    
    print("Total Books :", total)
    print("Available:", avail)
    print("Issued:", issued)
    print("Total Fine ₹:", fine)
    print("Total Students with Overdue: ", (~np.isnan(temp)).sum()) 
    
    total_r = ((user["Book_ID_1"].notna()).sum()+
              (user["Book_ID_2"].notna()).sum()+
              (user["Book_ID_3"].notna()).sum()+
              (library["Copies"]).sum()
             )
            
    avail_r = (library["Copies"]).sum()
    issued_r = total_r - avail_r
    fine_r = user["Fine"].sum()
    
    print("Total Books by count:", total_r)
    print("Total Books Available by count:", avail_r)
    print("Total Books Issued by Count:", issued_r)
    
    fig, ((ax1, ax2), (ay1, ay2)) = plt.subplots(2, 2, figsize=(12, 10))
    
    plt.subplots_adjust(wspace=0.6, hspace=0.4)
    
    ax1.pie([avail, issued], labels=["Available", "Issued"], autopct="%1.1f%%")
    ax1.set_title("""Available Books to Issue Books RATIO 
        By Availability""")
    
    ax2.bar(["Available", "Issued"],[avail, issued])
    ax2.set_title("Availability")
    ax2.set_xlabel("STATUS")
    ax2.set_ylabel("No. Of Books")
    
    total_r = ((user["Book_ID_1"].notna()).sum()+
              (user["Book_ID_2"].notna()).sum()+
              (user["Book_ID_3"].notna()).sum()+
              (library["Copies"]).sum()
             )
            
    avail_r = (library["Copies"]).sum()
    issued_r = total_r - avail_r
    fine_r = user["Fine"].sum()
    
    ay1.pie([avail_r, issued_r], labels=["Available", "Issued"], autopct="%1.1f%%")
    ay1.set_title('''Available Books by Issue Books RATIO
         By Count''')
    
    ay2.bar(["Available", "Issued"],[avail_r, issued_r])
    ay2.set_title("Availability By Count")
    ay2.set_xlabel("STATUS")
    ay2.set_ylabel("Total Count Of Books")

    plt.show()

    if (~np.isnan(temp)).sum() == 0:
        pass
    else:
        print(" \033[31mOVERDUE USERS: \033[0m", temp)
        ch = input("Remove this users (y/n): ")
        if ch.lower() == 'y':
            user_overdue()
        else:
            pass
    return login_admin()

# +++++ ADMIN +++++
def login_admin():
    global user, library, Book_ID
    try:
        task = int(input('''Enter your choice:

1. Create user
2. Delete user
3. Insert or update book
4. Delete book
5. Library statistics
6. Exit

Enter choice: '''))
        
        # +++++ TASK 1 - CREATE USER +++++
        if task == 1:
            create_user()
        # +++++ TASK 2 - DELETE USER +++++
        elif task == 2:
            delete_user()
        # +++++ TASK 3 - INSERT OR UPDATE BOOK +++++
        elif task == 3:
            book_insert()
        # +++++ TASK 4 - DELETE BOOK +++++
        elif task == 4:
            book_delete()
        # +++++ TASK 5 - LIBRARY STATUS +++++
        elif task == 5:
            lib_status()
        # +++++ TASK 6 - EXIT ++++++
        elif task == 6:
            print("---- THANK YOU ----")
            return 
        else:
            print("!!! INVALID ENTRY !!!")
            return login_admin()
    except ValueError:
            print("Invalid input!")
            return login_admin()

#---- Taking user ID ----
def userID():
    global user_attempt
    if user_attempt == 0:
        return   
    try:
        global User_ID
        User_ID = int(input("User ID: "))
        if User_ID in ex_user:
            print("!!! Due To OverDue Your Account has been Suspended !!!")
            return
        elif User_ID in U_ID_All:
            pwd = int(input("Password: "))
            if pwd == U_Pass_All[np.where(U_ID_All == User_ID)[0][0]]:
                login_user()
            else:
                print("!!! Password Not Matched !!!")
                user_attempt -= 1
                print(f"!!! {user_attempt} attempt left !!!")
                return userID()
        else:
            print("!!! ID Not Found !!!")
            user_attempt -= 1
            print(f"!!! {user_attempt} attempt left !!!")
            return userID()
    except ValueError:
        print("Invalid input!")
        user_attempt -= 1
        print(f"!!! {user_attempt} attempt left !!!")
        return userID()
#---Taking Admin ID ---
def adminID():
    global admin_attempt
    if admin_attempt == 0:
        return
    try:
        aid = int(input("Admin ID: "))
        if aid in A_ID_All:
            pwd = input("Password: ")
            if pwd == A_Pass_All[np.where(A_ID_All == aid)[0][0]]:
                login_admin()
            else:
                print("!!! Password Not Matched !!!")
                admin_attempt -= 1
                print(f"{admin_attempt} attempt left")
                return adminID()
        else:
            print("!!! ID Not Found !!!")
            admin_attempt -= 1
            print(f"{admin_attempt} attempt left")
            return adminID()
    except ValueError:
        print("Invalid input!")
        admin_attempt -= 1
        print(f"{admin_attempt} attempt left")
        return adminID()

# +++++ Admin/User +++++
def choice_select():
    try:
        choice = int(input("Login as 1.User or 2.Admin OR 3.Exit: "))
        if choice == 1:
            userID()
    
        elif choice == 2:
            adminID()

        elif choice == 3:
            return print("---THANK-YOU---")
        else:
            print("!!! INVALID ENTRY !!!")
            return choice_select()
    except ValueError:
        print("!!! Invalid input !!!")
        return choice_select()

#--- Calling function to run Program ----
save_data()
choice_select()
