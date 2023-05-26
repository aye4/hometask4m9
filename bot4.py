import sys
import json
from pathlib import Path
from collections import UserDict
from datetime import datetime
from re import search

DEFAULT_FILENAME = "ab.json"
RECORD_HEADER = (
    "## {:^20} {:^27} {:^30} {:^20}".format("User", "Birthday", "e-mail", "Phone number(s)")
    + "\n-- " + "-" * 20 + " " + "-" * 27 + " " + "-" * 30 + " " + "-" * 20
)
LINE = "-" * 30
BACK = "-"
A_MAIN = 0
A_ADD = 4
A_ADD_BD = 5
A_ADD_EM = 6
A_ADD_PH = 7
A_EDIT = 8
A_EDIT_ADD_PH = 9
A_EDIT_DEL_PH = 10
A_EDIT_UPD_EM = 11
A_EDIT_UPD_BD = 12
A_EDIT_DELETE = 13
MESSAGE = {
    A_MAIN: (
        "1 = Add new contact\n"
        + "2 = Show all (easy way to select one)\n"
        + "0 = Exit (Ctrl+C)\n"
        + LINE
        + "\nSelect an option or type some symbols to search by name/phone: "
    ),
    A_ADD: (
        LINE
        + "\nYou are about to add new contact.\n"
        + LINE
        + "\nYou may leave the black field to skip (press Enter),"
        + "\nEnter '-' command to go back to the previous value"
        + "\nCtrl+Z and Enter (or F6 and Enter) to finish"
        + "\nCtrl+C to exit/main menu\n"
        + LINE
        + "\nEnter a name (required): "
    ),
    A_ADD_BD: "Enter birthday (format is 'mm-dd' or 'yyyy-mm-dd', e.g. '05-21' or '1999-01-22'): ",
    A_ADD_EM: "Enter e-mail: ",
    A_ADD_PH: "Enter a list of 12-digit phone numbers separated by ' ' (e.g. 380501234567): ",
    A_EDIT: (
        "1 = Add new phone(s)\n"
        + "2 = Delete existing phone\n"
        + "3 = Update e-mail\n"
        + "4 = Update birthday\n"
        + "5 = Delete e-mail\n"
        + "6 = Delete birthday\n"
        + "7 = Delete contact\n"
        + "0 = Main menu (Ctrl+C)\n"
        + LINE
        + "\nSelect an option: "
    ),
    A_EDIT_ADD_PH: "\nEnter a list of 12-digit phone numbers separated by ' ' (e.g. 380501234567): ",
    A_EDIT_DEL_PH: LINE + "\nEnter row number for the phone to delete: ",
    A_EDIT_UPD_EM: "\nEnter e-mail: ",
    A_EDIT_UPD_BD: "\nEnter birthday (format is 'mm-dd' or 'yyyy-mm-dd', e.g. '05-21' or '1999-01-22'): ",
    A_EDIT_DELETE: "\nAre you sure you want to delete the selected contact (Y)?",
}
PAGE_SIZE = 5
PAGE_MESSAGE = "Press Enter to see next page or type a row number to select corresponding contact (Ctrl+C to exit): "
CTRL_C = "{~"
F6 = "}~"
MIN_YEAR = 1896
NUMBER_FORMAT = 1


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
        if len(value := str(value)) == 12 and value.isdigit():
            Field.value.fset(self, value)
        else:
            raise Exception(f"'{value}' is not a valid phone number")


class Email(Field):
    @Field.value.setter
    def value(self, value):
        if search(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", value):
            Field.value.fset(self, value)
        else:
            raise Exception(f"'{value}' is not a valid e-mail")


class Name(Field):
    ...


class Birthday(Field):
    @Field.value.setter
    def value(self, value):
        x = (
            str(MIN_YEAR) + "-" + value
            if search(r"^(0\d|1[012])-(0[1-9]|[12]\d|3[01])$", value)
            else value
        )
        try:
            birthday = datetime.strptime(x, "%Y-%m-%d")
        except ValueError:
            raise Exception(
                f"'{value}' does not match the expected date format 'yyyy-mm-dd'"
            )
        if not datetime.today().year > birthday.year >= MIN_YEAR:
            raise Exception(f"'{value}' is not a valid date")
        Field.value.fset(self, birthday)

    def replace_year(self, year: int) -> datetime:
        try:
            return self.value.replace(year=year)
        except ValueError:
            return datetime(year=year, month=2, day=28)

    def days_to_birthday(self) -> int:
        todays_date = datetime.today()
        birthday = self.replace_year(todays_date.year)
        if todays_date > birthday:
            birthday = self.replace_year(todays_date.year + 1)
        return (birthday - todays_date).days

    def std_str(self, mode=None) -> str:
        format_string = "%d %b" if self.value.year == MIN_YEAR else "%d %b %Y"
        if mode == NUMBER_FORMAT:
            format_string = "%m-%d" if self.value.year == MIN_YEAR else "%Y-%m-%d"
        return self.value.strftime(format_string)

    def __str__(self) -> str:
        return f"{self.std_str()} ({self.days_to_birthday()} days left)"


class Record:
    def __init__(self, name: Name, birthday=None, email=None, phone=None):
        self.name = name
        self.phone = []
        if phone:
            self.add_phone(phone)
        self.birthday = birthday
        self.email = email

    def is_phone(self, phone) -> bool:
        return phone.value in set(p.value for p in self.phone) if self.phone else False

    def add_phone(self, phone):
        add_counter = 0
        if isinstance(phone, list):
            for p in phone:
                if not self.is_phone(p):
                    self.phone.append(p)
                    add_counter += 1
        elif not self.is_phone(phone):
            self.phone.append(phone)
            add_counter = 1
        return add_counter

    def del_phone(self, phone):
        if self.is_phone(phone):
            self.phone.remove(phone)
            return True

    def is_in(self, search_string: str) -> bool:
        if len(search_string) <= 1:
            return False
        if search(search_string.lower(), self.name.value.lower()):
            return True
        if search_string.isdigit() and search(
            search_string, "!".join(p.value for p in self.phone)
        ):
            return True
        return False

    def __str__(self) -> str:
        phones = ", ".join(str(p) for p in self.phone)
        return f"{str(self.name):<20} {str(self.birthday):<27} {str(self.email):<30} {phones:<20}"

    def print_with_header(self):
        print("\n" + RECORD_HEADER + "\n   " + str(self) + "\n" + LINE + "\n")


class AddressBook(UserDict):
    def __init__(self, file_path=Path(DEFAULT_FILENAME)):
        super().__init__()
        self.file_path = file_path
        self.read_from_file()

    def add_record(self, record: Record, print_msg=True):
        self.data[record.name.value] = record
        self.save_changes = True
        if print_msg:
            print(f"\nContact '{record.name.value}' successfully added.\n")

    def delete_record(self, name):
        if name in self.data:
            del self.data[name]
            self.save_changes = True

    def __str__(self) -> str:
        return RECORD_HEADER + "\n".join(str(v) for v in self.values())

    def select(self, size=PAGE_SIZE, search_string=None):
        if search_string:
            names = sorted(k for k, v in self.data.items() if v.is_in(search_string))
        else:
            names = sorted(self.data.keys())
        for i in range(0, len(names), size):
            yield names[i : i + size]

    def from_dict(self, source_dict: dict):
        for k, v in source_dict.items():
            self.data[k] = Record(
                Name(v["name"]),
                birthday=Birthday(v["birthday"]) if v["birthday"] else None,
                email=Email(v["email"]) if v["email"] else None,
                phone=[Phone(x) for x in v["phone"]],
            )

    def read_from_file(self):
        self.save_changes = False
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.from_dict(json.load(f))

    def to_dict(self) -> dict:
        return {
            k: {
                "name": v.name.value,
                "birthday": v.birthday.std_str(mode=NUMBER_FORMAT)
                if v.birthday else None,
                "email": v.email.value if v.email else None,
                "phone": [p.value for p in v.phone],
            }
            for k, v in self.data.items()
        }

    def write_to_file(self):
        if self.save_changes:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f)
                self.save_changes = False


if len(sys.argv) > 1:
    pth = Path(sys.argv[1])
    if pth.is_dir():
        pth = pth / DEFAULT_FILENAME
else:
    pth = Path(DEFAULT_FILENAME)

d = AddressBook(pth)


def add_sequence(user_input: str, selected: Record, action: int):
    if (
        user_input == CTRL_C
        or action == A_ADD and (user_input == F6 or user_input == BACK)
    ):
        if len(d) == 0:
            exit("Good bye!")
        else:
            return A_MAIN, None
    elif user_input == F6:
        d.add_record(selected)
        selected.print_with_header()
        return A_MAIN, None
    elif user_input == BACK:
        if action == A_ADD_PH:
            return A_ADD_EM, selected
        elif action == A_ADD_EM:
            return A_ADD_BD, selected
        elif action == A_ADD_BD:
            return A_ADD, selected
    elif len(user_input):
        if action == A_ADD:
            if user_input in d:
                print(f"\n{user_input} is already in Contact list")
                return action, selected
            elif selected:
                selected.name.value = user_input
                selected.print_with_header()
                return A_ADD_BD, selected
            else:
                return A_ADD_BD, Record(Name(user_input))
        elif action == A_ADD_BD:
            try:
                birthday = Birthday(user_input)
            except Exception as e:
                print(e)
                return action, selected
            else:
                selected.birthday = birthday
                selected.print_with_header()
                return A_ADD_EM, selected
        elif action == A_ADD_EM:
            try:
                email = Email(user_input)
            except Exception as e:
                print(e)
                return action, selected
            else:
                selected.email = email
                selected.print_with_header()
                return A_ADD_PH, selected
        elif action == A_ADD_PH:
            for x in user_input.split():
                try:
                    p = Phone(x)
                except Exception as e:
                    print(e)
                    return action, selected
                else:
                    selected.add_phone(p)
            d.add_record(selected)
            selected.print_with_header()
            return A_MAIN, None
    elif action == A_ADD_BD:
        return A_ADD_EM, selected
    elif action == A_ADD_EM:
        return A_ADD_PH, selected
    elif action == A_ADD_PH:
        d.add_record(selected)
        return A_MAIN, None
    elif action == A_ADD:
        print("\nName cannot be skipped\n")
    return action, selected


def edit_sequence(user_input: str, selected: Record, action: int):
    if action == A_EDIT:
        if user_input == CTRL_C or user_input == "0":
            return A_MAIN, None
        elif user_input == "1":
            return A_EDIT_ADD_PH, selected
        elif user_input == "2":
            if selected.phone:
                if len(selected.phone) > 1:
                    print()
                    for i, p in enumerate(selected.phone):
                        print(f"{i} = {p.value}")
                    return A_EDIT_DEL_PH, selected
                else:
                    print(str(selected.phone[0]))
                    print(f"\nPhone '{selected.phone[0].value}' has been deleted.\n")
                    d[selected.name.value].phone = []
                    d.save_changes = True
            else:
                print("\nPhone list is empty\n")
        elif user_input == "3":
            print(f"", end="")
            return A_EDIT_UPD_EM, selected
        elif user_input == "4":
            return A_EDIT_UPD_BD, selected
        elif user_input == "5":
            if selected.email:
                print(f"\nE-mail '{selected.email.value}' has been deleted.\n")
                d[selected.name.value].email = None
                d.save_changes = True
        elif user_input == "6":
            if selected.birthday:
                print(f"\nBirthday '{selected.birthday.std_str()}' has been deleted.\n")
                d[selected.name.value].birthday = None
                d.save_changes = True
        elif user_input == "7":
            return A_EDIT_DELETE, selected
        else:
            print("\nUnrecognized command\n")
    elif user_input in (CTRL_C, F6):
        return A_EDIT, selected
    elif action == A_EDIT_ADD_PH:
        print()
        for x in user_input.split():
            try:
                p = Phone(x)
            except Exception as e:
                print(e)
            else:
                if d[selected.name.value].add_phone(p):
                    print(f"Phone '{x}' added.")
                    d.save_changes = True
                else:
                    print(f"Phone '{x}' already exists.")
    elif action == A_EDIT_DEL_PH:
        if user_input.isdigit() and 0 < int(user_input) < len(selected.phone):
            x = selected.phone[int(user_input)]
            print(f"\nPhone '{x.value}' has been deleted.\n")
            d[selected.name.value].del_phone(x)
            d.save_changes = True
    elif action == A_EDIT_UPD_EM:
        try:
            email = Email(user_input)
        except:
            print(f"\n'{user_input}' is not a valid e-mail.\n")
        else:
            d[selected.name.value].email = email
            d.save_changes = True
    elif action == A_EDIT_UPD_BD:
        try:
            birthday = Birthday(user_input)
        except Exception as e:
            print(e)
        else:
            print(f"\nBirthday {birthday.std_str()} added.\n")
            d[selected.name.value].birthday = birthday
            d.save_changes = True
    elif action == A_EDIT_DELETE and user_input.upper() == "Y":
        print(f"\nContact '{selected.name.value}' has been deleted\n")
        d.delete_record(selected.name.value)
        return A_MAIN, None
    return A_EDIT, selected


def main_menu(user_input: str, selected: Record, action: int):
    if user_input == "1":
        return A_ADD, None
    elif user_input == "0" or user_input == CTRL_C:
        d.write_to_file()
        exit("Good bye!")
    elif user_input in d:
        print(f"\nContact '{user_input}' selected\n")
        return A_EDIT, d[user_input]
    elif user_input == "2" or len(user_input) > 1:
        s = "" if user_input == "2" else user_input
        msg = (
            f"\nSearch pattern = '{user_input}'\n"
            if s
            else "\n'Show all contacts' selected\n"
        )
        print(msg)
        for x in d.select(PAGE_SIZE, s):
            print(RECORD_HEADER)
            for i, n in enumerate(x):
                print("{:>2} ".format(i) + str(d[n]))
            try:
                z = int(input(PAGE_MESSAGE).strip())
            except (ValueError, EOFError):
                continue
            except KeyboardInterrupt:
                print()
                return A_MAIN, None
            else:
                if 0 <= z < len(x):
                    print(f"\nContact '{x[z]}' selected\n")
                    return A_EDIT, d[x[z]]
        print(LINE)
    else:
        print("\nUnrecognized command\n")
    return A_MAIN, None


menu_functions = {
    A_MAIN: main_menu,
    A_ADD: add_sequence,
    A_ADD_BD: add_sequence,
    A_ADD_EM: add_sequence,
    A_ADD_PH: add_sequence,
    A_EDIT: edit_sequence,
    A_EDIT_ADD_PH: edit_sequence,
    A_EDIT_DEL_PH: edit_sequence,
    A_EDIT_UPD_EM: edit_sequence,
    A_EDIT_UPD_BD: edit_sequence,
    A_EDIT_DELETE: edit_sequence,
}


if __name__ == "__main__":
    action = A_MAIN
    selected = None
    while True:
        msg = ""
        if action == A_MAIN:
            cnt = f"\n[{len(d)} contacts]" if len(d) else "\nContact list is empty"
            print(cnt + "\n" + LINE)
            if len(d) == 0:
                action = A_ADD
        elif action == A_EDIT:
            selected.print_with_header()
        try:
            s = input(MESSAGE[action]).strip()
        except EOFError:
            s = F6
        except KeyboardInterrupt:
            s = CTRL_C
            print()
        finally:
            action, selected = menu_functions[action](s, selected, action)
