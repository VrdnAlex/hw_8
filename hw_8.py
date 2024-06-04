import pickle
from collections import UserDict
from datetime import timedelta, datetime


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)  
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError('Cant be empty')
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError('It must contain 10 digits')
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    @staticmethod
    def input_error(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                print(f"Input error: {e}")

        return wrapper

    @input_error
    def add(self, args, book):
        name, phone = args
        if name in book.contacts:
            # Вже існує контакт з таким ім'ям, оновлюємо номер телефону
            book.contacts[name] = phone
            return "Contact updated."
        else:
            # Новий контакт
            book.contacts[name] = phone
            return "Contact added."

    @input_error
    def change(self, args, book):
        name, new_phone = args
        if name in book.contacts:
            # Змінюємо телефонний номер для вказаного контакту
            book.contacts[name] = new_phone
            return "Phone number changed."
        else:
            return "Contact not found."

    @input_error
    def phone(self, args, book):
        name = args[0]
        if name in book.contacts:
            # Показуємо телефонний номер для вказаного контакту
            return f"The phone number for {name} is {book.contacts[name]}."
        else:
            return "Contact not found."

    @input_error
    def all_contacts(self, book):
        if book.contacts:
            # Показуємо всі контакти
            return "\n".join([f"{name}: {phone}" for name, phone in book.contacts.items()])
        else:
            return "No contacts found."

    @input_error
    def add_phone(self, value):
        phone = Phone(value)
        self.phones.append(phone)

    @input_error
    def add_birthday(self, value):
        try:
            self.birthday = Birthday(value)
            print(f"Birthday added for {self.name}.")
        except ValueError as e:
            print(e)

    @input_error
    def show_birthday(self):
        if self.birthday:
            print(f"{self.name}'s birthday is on {self.birthday}.")
        else:
            print("Birthday not set.")

    @input_error
    def birthday(self):
        return self.birthday

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {', '.join(str(phone.value) for phone in self.phones)}"


class AddressBook(UserDict):

    def __init__(self):
        super().__init__()
        self.records = []

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        next_week = datetime.now() + timedelta(days=7)
        for record in self.data.values():
            if record.birthday is not None and record.birthday.value.month == next_week.month \
                    and record.birthday.value.day >= next_week.day:
                upcoming_birthdays.append(record.name.value)
        return upcoming_birthdays

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def change(self, args):
        name, new_phone = args
        record = self.find(name)
        if record:
            record.add_phone(new_phone)
            return "Phone number changed."
        else:
            return "Contact not found."

    def phone(self, args):
        name = args[0]
        record = self.find(name)
        if record:
            return f"The phone number for {name} is {', '.join(record.phones)}."
        else:
            return "Contact not found."

    def all_contacts(self):
        if self.data:
            return "\n".join([str(record) for record in self.data.values()])
        else:
            return "No contacts found."

    def save_data(self, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load_data(cls, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return cls()


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def main():
    book = AddressBook.load_data()  # Завантаження данних при запуску
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            book.save_data()  # Зберігаємо адресну книгу перед виходом
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            if len(args) != 2:
                print("Invalid number of arguments. Please provide name and phone.")
            else:
                name, phone = args
                record = Record(name)
                record.add_phone(phone)
                book.add_record(record)
                print("Contact added.")

        elif command == "change":
            if len(args) != 2:
                print("Invalid number of arguments. Please provide name and new phone.")
            else:
                print(book.change(args))

        elif command == "phone":
            if len(args) != 1:
                print("Invalid number of arguments. Please provide name.")
            else:
                print(book.phone(args))

        elif command == "all":
            print(book.all_contacts())

        elif command == "add-birthday":
            if len(args) != 2:
                print("Invalid number of arguments. Please provide name and birthday in format DD.MM.YYYY.")
            else:
                name, birthday = args
                record = book.find(name)
                if record:
                    record.add_birthday(birthday)
                else:
                    print("Contact not found.")

        elif command == "show-birthday":
            if len(args) != 1:
                print("Invalid number of arguments. Please provide name of the contact.")
            else:
                name = args[0]
                record = book.find(name)
                if record:
                    record.show_birthday()
                else:
                    print("Contact not found.")

        elif command == "birthdays":
            for record in book.data.values():
                record.show_birthday()

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
