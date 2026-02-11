import random

class Admin:
    def __init__(self):
        self.levels = {}

    def create_level(self, level_name, min, max, attempts):
        self.levels[level_name] = [min, max, attempts]

    def update_level(self, level_name, min, max, attempts):
        if level_name in self.levels:
            if min:
                self.levels[level_name][0] = min
            if max:
                self.levels[level_name][1] = max
            if attempts:
                self.levels[level_name][2] = attempts
        else:
            print("Level not found.")

    def delete_level(self, level_name):
        if level_name in self.levels:
            del self.levels[level_name]
        else:
            print("Level not found.")

    def view_levels(self):
        if not self.levels:
            print("No levels created yet.")
        for level, details in self.levels.items():
            print(f"Level: {level}, Range: {details[0]}-{details[1]}, Attempts: {details[2]}")


class Player:
    def __init__(self, admin):
        self.admin = admin

    def game(self, level_name):
        if level_name not in self.admin.levels:
            print(f"Level '{level_name}' does not exist!")
            return

        min,max,attempts = self.admin.levels[level_name]
        number_to_guess = random.randint(min, max)

        print(f"Welcome to level '{level_name}'!")
        print(f"Guess a number between {min} and {max}")

        while attempts > 0:
            try:
                guess = int(input("Enter your guess: "))
            except ValueError:
                print("Please enter a valid number.")
                continue

            if guess == number_to_guess:
                print("Congratulations! You guessed the number!")
                return
            elif guess < number_to_guess:
                print("Too low!")
            else:
                print("Too high!")

            attempts -= 1
            print(f"Attempts remaining: {attempts}")

        print(f"Game over! The number was {number_to_guess}.")

admin_user = Admin()
player_user = Player(admin_user)
print("Welcome to the Number Guessing Game")

while True:
    print("\nMenu:")
    print("1. Admin")
    print("2. Player")
    print("3. Exit")

    choice = int(input("Enter your choice (1-3): "))
    match choice:
        case 1:
            while True:
                print("\nAdmin Menu:")
                print("1. Create Level")
                print("2. Update Level")
                print("3. Delete Level")
                print("4. View Levels")
                print("5. Back")

                admin_choice = int(input("Enter your choice (1-5): "))

                match admin_choice:
                    case 1:
                        level = input("Level name: ")
                        min = int(input("Min number: "))
                        max = int(input("Max number: "))
                        attempts = int(input("Attempts: "))
                        admin_user.create_level(level, min, max, attempts)

                    case 2:
                        level = input("Level name: ")
                        min = input("New min: ")
                        max = input("New max : ")
                        attempts = input("New attempts: ")

                        admin_user.update_level(level,
                            int(min) if min else None,
                            int(max) if max else None,
                            int(attempts) if attempts else None)

                    case 3:
                        admin_user.delete_level(input("Level name: "))

                    case 4:
                        admin_user.view_levels()

                    case 5:
                        break

        case 2:
            level = input("Enter level name to play: ")
            player_user.game(level)

        case 3:
            print("You've left the game.")
            break
