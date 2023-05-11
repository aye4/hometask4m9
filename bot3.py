from collections import UserDict
from datetime import datetime
from re import search

RECORD_HEADER = "{:^20} {:^27} {:^20}".format("User", "Birthday", "Phone number(s)") + "\n" + "-" * 20 + " " + "-" * 27 + " " + "-" * 20 + "\n"
N = 10

class Field:
    def __init__(self, value=None):
       self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self) -> str:
        return self.value

class Phone(Field):
    @Field.value.setter
    def value(self, value):
        if len(value) == 12 and value.isdigit():
            Field.value.fset(self, value)
        else:
            raise Exception(f"'{value}' is not a valid phone number")


class Name(Field):
    ...


class Birthday(Field):
    @Field.value.setter
    def value(self, value):
        if search(r"^(0\d|1[012])-(0[1-9]|[12]\d|3[01])$", value):
            d = datetime.strptime("1900-" + value, "%Y-%m-%d")
        elif search(r"^(19\d\d|20[012]\d)-(0\d|1[012])-(0[1-9]|[12]\d|3[01])$", value):
            d = datetime.strptime(value, "%Y-%m-%d")
            if not datetime(year=1900, month=1, day=1) < d < datetime.now():
                raise Exception(f"'{value}' is not a valid date")
        else:
            raise Exception("Birthday was not specified")
        Field.value.fset(self, d)

    def __str__(self) -> str:
        return self.value.strftime("%d %b") if self.value.year == 1900 else self.value.strftime("%d %b %Y")


def str_days_left(days: int) -> str:
    return "" if days is None else f" ({days} days left)"


class Record:
    def __init__(self, name: Name, birthday=None, phone=None):
        self.name = name
        self.phone = []
        self.add_phone(phone)
        self.birthday = birthday

    def add_phone(self, phone) -> int:
        z = set(p.value for p in self.phone)
        n = 0
        if type(phone) in (list, tuple):
            for p in phone:
                if p.value not in z:
                    self.phone.append(p)
                    z.add(p.value)
                    n += 1
        else:
            if phone.value not in z:
                self.phone.append(phone)
                n = 1
        return n

    def chg_phone(self, phone) -> int:
        if phone:
            self.phone = []
            return self.add_phone(phone)

    def del_phone(self, phone) -> int:
        n = 0
        if phone:
            phone_set = {x.value for x in phone} if type(phone) in (list, tuple) else {phone.value}
            for p in self.phone:
               if p.value in phone_set:
                   self.phone.remove(p)
                   n += 1
        return n

    def days_to_birthday(self) -> int:
        if self.birthday:
            n = datetime.now()
            m = self.birthday.value.month
            d = self.birthday.value.day
            y = n.year
            if m < n.month or m == n.month and d < n.day:
                y += 1
            return (datetime(year=y, month=m, day=d) - n).days

    def __str__(self) -> str:
        return "{:<20} {:<27} {:<20}".format(self.name, str(self.birthday) + str_days_left(self.days_to_birthday()), ", ".join(str(p) for p in self.phone))


class IterPage:
    def __init__(self, obj, page_length):
        self.iter_obj = iter(obj)
        self.page_length = page_length

    def __iter__(self): 
        return self

    def __next__(self):
       r = []
       while len(r) < self.page_length:
           try:
               r.append(next(self.iter_obj))
           except StopIteration:
               if r:
                   return r
               else:
                   raise StopIteration
       return r


class AddressBook(UserDict):
    def add_record(self, name, birthday=None, phone=None) -> str:
        if not name:
            return "Username should be specified."
        if name in self.data:
            s = ""
            if birthday and not self.data[name].birthday:
                self.data[name].birthday = birthday
                s = "birthday added"
            n = self.data[name].add_phone(phone)
            if n:
                s += f", {n} phone number(s) added"
            return f"{s} for user '{name}'." if s else "Check birthday and/or phone number(s)"
        else:
            self.data[name] = Record(name, birthday, phone)
            n = len(self.data[name].phone)
            s = f"{n} phone number(s)" if n else ""
            s += "" if not birthday else " and a birthday" if s else "a birthday"
            if s:
                s = " with " + s
            return f"Contact '{name}' added{s}."

    def __str__(self) -> str:
        return RECORD_HEADER + "\n".join(str(v) for v in self.values())

    def iterator(self, page_length):
        return IterPage(self, page_length)


d = AddressBook()


def input_error(f):
    def wrapper(*args):
        try:
            r = f(*args)
        except TypeError:
            r = "Please specify username and phone number"
        except KeyError:
            r = "No such username."
        except Exception as e:
            print("Exception!!!", e)
        return r
    return wrapper


def process_args(*args):
    birthday = None
    try:
        birthday = Birthday(args[0])
    except Exception as e:
        if str(e).endswith(" is not a valid date"):
            print(e)
            args = args[1:]
    else:
        args = args[1:]
    phone = []
    while args:
        try:
            phone.append(Phone(args[0]))
        except Exception as e:
            print(e)
        finally:
            args = args[1:]
    return birthday, phone


def add_h(user: str, *args) -> str:
    birthday, phone = process_args(*args)
    return d.add_record(user, birthday, phone)


def phone_h(user: str, *_) -> str:
    return RECORD_HEADER + str(d[user])


def change_h(user: str, *args) -> str:
    birthday, phone = process_args(*args)
    s = ""
    if birthday:
        d[user].birthday = birthday
        s = ", birthday updated"
    n = 0
    if phone:
        n = d[user].chg_phone(phone)
        s += f", {n} phone number(s) updated"
    return f"Contact '{user}' changed{s}." if s else "Check birthday and/or phone number(s)"


def delete_h(user: str, *args) -> str:
    birthday, phone = process_args(*args)
    s = ""
    if birthday is None and not phone:
        del d[user]
        return f"Contact '{user}' deleted."
    if birthday:
        if d[user].birthday.value == birthday.value:
            d[user].birthday = None
            s = ", birthday deleted"
    if phone:
        n = d[user].del_phone(phone)
        if n:
            s = ", {n} phone number(s) deleted"
    return f"Contact '{user}' changed{s}." if s else "Check birthday and/or phone number(s)"


def show_all(*_) -> str:
    for x in d.iterator(N):
        if x:
            print(RECORD_HEADER + "\n".join(str(d[r]) for r in x))
            if len(x) == N:
                s = input("Press Enter to see the next page ('stop' to finish)")
                if s.lower() == "stop":
                    break
    return ""


def exit_h(*_) -> str:
    return "Good bye!"


def help_h(*_) -> str:
    return (
    "\nValid commands are:\n"
    + "-" * 20 + "\n"
    + "add <user> [birthday] <phone|phone list>\n"
    + "change <user> [birthday] <phone|phone list>\n"
    + "delete <user> [birthday] <phone|phone list>\n"
    + "phone <user>\n"
    + "show all\n"
    + "close\n"
    + "exit\n"
    + "good bye\n"
    + "hello\n"
    + "-" * 10 + "\n"
    + "[birthday] is an optional 5-symbol parameter; format is mm-dd, e.g. 05-21\n"
    + "NB: 10-symbol full date is also accepted, e.g. 1999-01-22\n"
    + "phone numbers should consist of 12 digits only, e.g. 380501234567\n"
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
