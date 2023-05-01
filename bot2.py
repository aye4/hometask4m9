from collections import UserDict


class Field:
    def __init__(self, value=None):
       self.__value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Phone(Field):
    def __str__(self) -> str:
        return self.value
    

class Name(Field):
    def __str__(self) -> str:
        return self.value


class Record:
    def __init__(self, name, phone=None):
        self.name = Name(name)
        self.phone = []
        self.add_phone(phone)

    def add_phone(self, phone) -> int:
        z = set(p.value for p in self.phone)
        n = 0
        if type(phone) in (list, tuple):
            for p in phone:
                if p not in z:
                    self.phone.append(Phone(p))
                    z.add(p)
                    n += 1
        else:
            if phone not in z:
                self.phone.append(Phone(phone))
                n = 1
        return n

    def chg_phone(self, phone) -> int:
        self.phone = []
        return self.add_phone(phone)

    def del_phone(self, phone) -> int:
        n = 0
        for p in self.phone:
            if p.value in phone:
                self.phone.remove(p)
                n += 1
        return n

    def __str__(self) -> str:
        return (
            "{:^20} {:^20}".format("User", "Phone number(s)") + "\n"
            + "-" * 20 + " " + "-" * 20 + "\n"
            + "{:<20} {:<20}".format(self.name.value, ', '.join(p.value for p in self.phone))
        )


class AddressBook(UserDict):
    def add_record(self, name, phone=None) -> str:
        if not name:
            return "Username should be specified."
        if name in self.data:
            return f"{self.data[name].add_phone(phone)} phone number(s) added for user {name}."
        else:
            self.data[name] = Record(name, phone)
            return f"Contact '{name}' added with {len(self.data[name].phone)} phone number(s)."

    def __str__(self) -> str:
        return (
            "{:^20} {:^20}".format("User", "Phone number(s)") + "\n"
            + "-" * 20 + " " + "-" * 20 + "\n"
            + "\n".join("{:<20} {:<20}".format(k, ', '.join(p.value for p in v.phone)) for k, v in d.items())
        )


d = AddressBook()


def input_error(f):
    def wrapper(*args):
        try:
            r = f(*args)
        except TypeError:
            r = "Please specify username and phone number"
        except KeyError:
            r = "No such username."
        return r

    return wrapper


#@input_error
def add_h(user: str, *phone) -> str:
    return d.add_record(user, phone)


@input_error
def phone_h(user: str, *_) -> str:
    return str(d[user])


@input_error
def change_h(user: str, *phone) -> str:
    n = d[user].chg_phone(phone)
    return f"Contact '{user}' changed, {n} phone number(s) updated." if n else "Check phone number(s)"


@input_error
def delete_h(user: str, *phone) -> str:
    n = d[user].del_phone(phone)
    return f"Contact '{user}' changed, {n} phone number(s) deleted." if n else "Check phone number(s)"


def show_all(*_) -> str:
    return str(d)


def exit_h(*_) -> str:
    return "Good bye!"


def help_h(*_) -> str:
    return (
    "Valid commands are:\n"
    + "-" * 20 + "\n"
    + "add <user> <phone|phone list>\n"
    + "change <user> <phone|phone list>\n"
    + "delete <user> <phone|phone list>\n"
    + "phone <user>\n"
    + "show all\n"
    + "close\n"
    + "exit\n"
    + "good bye\n"
    + "hello\n"
    + "-" * 20 + "\n"
)


commands = {
    "add":add_h,
    "exit":exit_h,
    "help":help_h,
    "hello":lambda *_: "How can I help you?",
    "close":exit_h,
    "phone":phone_h,
    "change":change_h,
    "delete":delete_h,
    "show all":show_all,
    "good bye":exit_h,
}

@input_error
def parse_command(s: str) -> str:
    r = "Unrecognized command. Try typing 'help'."
    if s:
        x = s.split()
        z = x[0].lower()
        if z in commands:
            r = commands[z](*x[1:])
        else:
            z = ' '.join(x[:2]).lower()
            if z in commands:
                r = commands[z](*x[2:])
    return r


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
