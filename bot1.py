d = {}


def input_error(f):
    def wrapper(*args):
        try:
            r = f(*args)
        except KeyError:
            r = "No such username."
        #        except IndexError:
        #            r = ""
        except ValueError:
            r = "Check the phone number (only digits allowed)."
        except TypeError:
            r = "Please specify username and phone number"
        return r

    return wrapper


@input_error
def add_h(user: str, phone: str) -> str:
    if user in d:
        return f"User '{user}' is already in contact list."
    p = int(phone)
    d[user] = phone
    return f"Contact '{user}' added, phone number = {phone}"


@input_error
def change_h(user: str, phone: str) -> str:
    x = d[user]
    p = int(phone)
    d[user] = phone
    return f"Contact '{user}' changed from {x} to {phone}"


@input_error
def phone_h(user: str) -> str:
    return d[user]


@input_error
def parse_command(s: str) -> str:
    if s[:3].lower() == "add":
        return add_h(*s[4:].split(" "))
    elif s[:4].lower() == "exit":
        return "Good bye!"
    elif s[:4].lower() == "help":
        return "Valid commands are:\n---\nadd <user> <phone>\nchange <user> <phone>\nphone <user>\nshow all\nclose\nexit\ngood bye\n---"
    elif s[:5].lower() == "close":
        return "Good bye!"
    elif s[:5].lower() == "phone":
        return phone_h(s[6:])
    elif s[:6].lower() == "change":
        return change_h(*s[7:].split(" "))
    elif s[:8].lower() == "show all":
        return (
            "{:^20} {:^12}".format("User", "Phone") + "\n"
            + "-" * 20 + " " + "-" * 12 + "\n"
            + "\n".join("{:<20} {:<12}".format(k, v) for k, v in d.items())
        )
    elif s[:8].lower() == "good bye":
        return "Good bye!"
    else:
        return "Unrecognized command. Try typing 'help'."


if __name__ == "__main__":
    while True:
        try:
            s = input(f"{len(d)} contacts >").strip()
        except EOFError:
            x = "Unrecognized command. Try typing 'help'."
        except KeyboardInterrupt:
            x = "\nUnrecognized command. Try typing 'help'."
        else:
            x = parse_command(s)
        print(x)
        if x == "Good bye!":
            break
