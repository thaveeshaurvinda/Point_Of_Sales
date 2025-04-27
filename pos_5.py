"""
original an final
search by id
generate only tax transaction file
display upper,lower,digits and dots with checksum in tax file
do not show them on the basket
with item code and name dictionary
"""

import sys
import datetime
import csv
import os

class PosSystem:
    def __init__(self):
        self.basket = []
        self.tax_file = "tax_transactions.csv"
        self.transaction_id_counter = self.load_last_transaction_id()
        self.inventory = {
            "CC": "Chocolate Cupcake",
            "VC": "Vanilla Cupcake",
            "SC": "Strawberry Cupcake",
            "BC": "Brownie Cupcake",
            "MC": "Muffin Cupcake"
        }

    def load_last_transaction_id(self):
        if os.path.exists(self.tax_file) and os.path.getsize(self.tax_file) > 0:
            with open(self.tax_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)  # Read the file as CSV using column names
                if "transaction_id" in reader.fieldnames:
                    id_list = []
                    for row in reader:
                        if row["transaction_id"].isdigit():  # Check if the ID is a number
                            id_list.append(int(row["transaction_id"]))
                    if id_list:
                        return max(id_list) + 1
        return 1

    def calculate_transaction_checksum(self, transaction_line):
        lowercase_count = 0
        uppercase_count = 0
        digit_or_dot_count = 0

        for character in transaction_line:
            if character.isupper():
                uppercase_count += 1
            elif character.islower():
                lowercase_count += 1
            elif character.isdigit() or character == '.':
                digit_or_dot_count += 1

        checksum = uppercase_count + lowercase_count + digit_or_dot_count
        return uppercase_count, lowercase_count, digit_or_dot_count, checksum

    def user_input_validation(self):
        while True:
            user_input = input("Enter item (Item Code, Internal Price, Discount, Sale Price, Quantity): ")
            if "," not in user_input:
                print("Invalid input. Use commas.")
                continue

            product_details = user_input.split(",")

            if len(product_details) != 5:
                print("Please enter exactly 5 values.")
                continue

            item_code = product_details[0].strip()
            if item_code not in self.inventory:
                print("Invalid item code. Not found in inventory.")
                continue

            try:
                product_details[0] = item_code
                product_details[1] = float(product_details[1])
                product_details[2] = float(product_details[2])
                product_details[3] = float(product_details[3])
                product_details[4] = int(product_details[4])
                break
            except ValueError:
                print("Invalid data type. Try again.")

        self.input_array = product_details

    def add_item(self):
        self.user_input_validation()
        item_code = self.input_array[0]
        item_name = self.inventory[item_code]
        internal_price = float(self.input_array[1])
        discount = float(self.input_array[2])
        sale_price = float(self.input_array[3])
        quantity = int(self.input_array[4])
        line_total = sale_price * quantity * (1 - discount / 100)

        line = item_name + "," + str(internal_price) + "," + str(discount) + "," + str(sale_price) + "," + str(quantity) + "," + str(line_total)
        uppercase_count, lowercase_count, digit_or_dot_count, checksum = self.calculate_transaction_checksum(line)

        item = {
            "item_name": item_name,
            "internal_price": internal_price,
            "discount": discount,
            "sale_price": sale_price,
            "quantity": quantity,
            "line_total": line_total,
            "uppercase": uppercase_count,
            "lowercase": lowercase_count,
            "digits_and_dots": digit_or_dot_count,
            "checksum": checksum
        }

        self.basket.append(item)
        print("Item added successfully!")
        self.display_basket()

    def display_basket(self):
        if not self.basket:
            print("Basket is empty.")
        else:
            print("\nCurrent Basket:")
            print("--------------------------------------------------------------------------")
            print("Line | Item Name       | Internal Price | Discount | Sale Price | Quantity")
            print("--------------------------------------------------------------------------")

            for index, item in enumerate(self.basket):
                print(f"{index:<4} | {item['item_name']:<15} | {item['internal_price']:<14} | "f"{item['discount']:<8} | {item['sale_price']:<10} | {item['quantity']}")

    def delete_item(self):
        self.display_basket()
        try:
            line_num = int(input("Enter line number to delete: "))
            if 0 <= line_num < len(self.basket):
                del self.basket[line_num]
                print("Item deleted successfully.")
            else:
                print("Invalid line number.")
        except ValueError:
            print("Invalid input. Enter a number.")

    def update_basket(self):
        self.display_basket()
        try:
            line_num = int(input("Enter line number to update: "))
            if 0 <= line_num < len(self.basket):
                self.user_input_validation()
                item_code = self.input_array[0]
                item_name = self.inventory[item_code]
                internal_price = float(self.input_array[1])
                discount = float(self.input_array[2])
                sale_price = float(self.input_array[3])
                quantity = int(self.input_array[4])
                line_total = sale_price * quantity * (1 - discount / 100)

                line = item_name + "," + str(internal_price) + "," + str(discount) + "," + str(sale_price) + "," + str(quantity) + "," + str(line_total)
                uppercase_count, lowercase_count, digit_or_dot_count, checksum = self.calculate_transaction_checksum(line)

                self.basket[line_num] = {
                    "item_name": item_name,
                    "internal_price": internal_price,
                    "discount": discount,
                    "sale_price": sale_price,
                    "quantity": quantity,
                    "line_total": line_total,
                    "uppercase": uppercase_count,
                    "lowercase": lowercase_count,
                    "digits_and_dots": digit_or_dot_count,
                    "checksum": checksum
                }

                print("Basket item updated.")
            else:
                print("Invalid line number.")
        except ValueError:
            print("Invalid input. Enter a number.")

    def generate_bill(self):
        if not self.basket:
            print("Basket is empty.")
            return

        grand_total = 0
        transaction_id = self.transaction_id_counter
        bill_date = datetime.datetime.now().strftime("%Y-%m-%d")

        print("\n-------- BILL --------")
        print(f"Transaction ID: {transaction_id}")
        print(f"Date: {bill_date}")
        print("----------------------")

        for idx, item in enumerate(self.basket, 1):
            print(f"{idx}. Item Name: {item['item_name']} | Quantity: {item['quantity']} | "
                  f"Sale Price: {item['sale_price']} | Discount: {item['discount']}% | "
                  f"Line Total: {item['line_total']:.2f}")
            grand_total += item["line_total"]

        print("----------------------")
        print(f"Grand Total: {grand_total:.2f}")
        print("----------------------")

        self.save_to_tax_file(transaction_id, bill_date)
        self.transaction_id_counter += 1
        self.basket.clear()
        print("Transaction saved to tax file and basket cleared.")

    def save_to_tax_file(self, transaction_id, bill_date):
        file_exists = os.path.isfile(self.tax_file) and os.stat(self.tax_file).st_size > 0

        with open(self.tax_file, "a", newline='') as csvfile:
            fieldnames = ["transaction_id", "date", "item_name", "internal_price", "discount", "sale_price",
                          "quantity", "line_total", "uppercase", "lowercase", "digits_and_dots", "checksum"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            for item in self.basket:
                row = item.copy()
                row["transaction_id"] = transaction_id
                row["date"] = bill_date
                writer.writerow(row)

    def search_bill(self):
        transaction_id = input("Enter transaction ID to search: ").strip()
        found = False

        if os.path.exists(self.tax_file) and os.path.getsize(self.tax_file) > 0:
            with open(self.tax_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)

                if "transaction_id" not in reader.fieldnames:
                    print("Tax file does not contain transaction IDs.")
                    return

                print(f"\nSearch Results for Transaction ID: {transaction_id}")
                print("Date | Item Name | Quantity | Sale Price | Discount | Line Total")

                for row in reader:
                    if row["transaction_id"] == transaction_id:
                        print(row["date"], "|", row["item_name"], "| Qty:", row["quantity"], "| Sale Price:",
                              row["sale_price"], "| Discount:", row["discount"] + "%", "| Line Total:",
                              row["line_total"])
                        found = True

        if not found:
            print("Transaction ID not found.")

    def menu(self):
        print("\nPOS System Menu:")
        print("1. Add Item to Basket")
        print("2. Delete Item from Basket")
        print("3. Update Item in Basket")
        print("4. Show Current Basket")
        print("5. Generate Bill and Save to Tax File")
        print("6. Search Transaction by ID")
        print("7. Exit")

    def main(self):
        while True:
            self.menu()
            try:
                choice = int(input("Enter your choice: "))
                if choice == 1:
                    self.add_item()
                elif choice == 2:
                    self.delete_item()
                elif choice == 3:
                    self.update_basket()
                elif choice == 4:
                    self.display_basket()
                elif choice == 5:
                    self.generate_bill()
                elif choice == 6:
                    self.search_bill()
                elif choice == 7:
                    print("Exiting POS system.")
                    sys.exit()
                else:
                    print("Invalid option. Choose between 1–7.")
            except ValueError:
                print("Enter a valid number.")

if __name__ == "__main__":
    pos = PosSystem()
    pos.main()

