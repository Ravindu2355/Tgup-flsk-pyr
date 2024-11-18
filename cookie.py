import json


cookiefile= 'cookies.json'

def r_cookies():
    try:
        with open(cookiefile, 'r') as file:
            cookies = json.load(file)
            return cookies
    except FileNotFoundError:
        print("Cookie file not found. Returning empty dictionary.")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON. Returning empty dictionary.")
        return {}

def w_cookies( cookies):
    with open(cookiefile, 'w') as file:
        json.dump(cookies, file, indent=4)
    print("Cookies have been written to the file.")

def clear_cookies():
    with open(cookiefile, 'w') as file:
        json.dump({}, file)
    print("Cookies have been cleared.")
