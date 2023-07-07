import shelve

# this file contains functions which are used in the main file


# this function saves the image to the database
def save_to_db(filepath):
    try:
        image_file = shelve.open("images")
        images = image_file['images']
        images.append(filepath)
        image_file['images'] = images
    except:
        images = []
        images.append(filepath)
        image_file['images'] = images


# this function checks the username and password of the admin
def validate_login(username, password):
    try:
        user_file = shelve.open("users")
        users = user_file['users']
        for user in users:
            if user[0] == username and user[2] == password:
                return True
        return False

    except:
        return False


# this function checks if the user is already taken or not
def check_username(username):
    try:
        user_file = shelve.open("users")
        users = user_file['users']
        for user in users:
            if user[0] == username:
                return True
        return False

    except:
        return False

# this function checks if the email is already taken or not


def check_email(email):
    try:
        user_file = shelve.open("users")
        users = user_file['users']
        for user in users:
            if user[1] == email:
                return True
        return False

    except:
        return False


# this function is used to get the user details and then modify them in databasr
def modify_user(previous_username, username, email, password, address, postal_code):
    try:
        # open the database
        user_file = shelve.open("users")
        users = user_file['users']
        i = 0
        is_changed = False
        # loop through the users and check if the username is already taken
        for user in users:
            if user[0] == previous_username:
                is_changed = True
                break
            i += 1
        # make the changes
        if is_changed:
            users[i][0] = username
            users[i][1] = email
            users[i][2] = password
            users[i][4] = address
            users[i][5] = postal_code
            user_file['users'] = users
    except:
        users = []
        new_user = [username, email, password, address, postal_code]
        users.append(new_user)
        user_file['users'] = users


def modify_user_pic(username, imagefn):
    try:
        user_file = shelve.open("users")
        users = user_file['users']
        is_changed = False
        i = 0
        for user in users:
            if user[0] == username:
                is_changed = True
                break
            i += 1
        if is_changed:
            users[i][3] = imagefn
        user_file['users'] = users
        user_file.close()
    except:
        print("they are no users available.")


# function is used to validate the registration
# it checks if the username or email is already taken or not
def validate_registration(email, username):
    try:
        user_file = shelve.open("users")
        users = user_file['users']
        is_username = False
        is_emailAddress = False
        for user in users:
            if user[0] == username:
                is_username = True
            if user[1] == email:
                is_emailAddress = True
        if is_username or is_emailAddress:
            return False
        else:
            return True

    except:
        return True


# this function is used to add the user to the database
def add_user(username, email, password, address, postal_code):
    try:
        user_file = shelve.open("users")
        users = user_file['users']
        new_user = [username, email, password,
                    "default.jpeg", address, postal_code]
        users.append(new_user)
        user_file['users'] = users
    except:
        print("Error")
        users = []
        new_user = [username, email, password,
                    'default.jpeg', address, postal_code]
        users.append(new_user)
        user_file['users'] = users


# this function is used to add the product to the database
def add_prod(name, price, description, quantity, image, sales):
    try:
        prod = shelve.open("products")
        product = prod['prods']
        new_prod = [name, price, description, quantity, image, sales]
        product.append(new_prod)
        prod['prods'] = product
        prod.close()
    except:
        print("Error")
        product = []
        new_prod = [name, price, description, quantity, image, sales]
        product.append(new_prod)
        prod['prods'] = product
        prod.close()
