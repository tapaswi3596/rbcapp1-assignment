import csv
import os


INPUT_FILE = "Assignment python.csv"
OUTPUT_FILE = "filtered_sales.csv"


def read_sales_data(filename):
    with open(filename, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def calculate_price_per_sqft(row):
    price = float(row["price"])
    square_feet = float(row["sq__ft"])

    if square_feet <= 0:
        return None

    return price / square_feet


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file not found: {INPUT_FILE}")
        return

    rows = read_sales_data(INPUT_FILE)

    valid_sales = []
    price_per_sqft_values = []

    for row in rows:
        price_per_sqft = calculate_price_per_sqft(row)

        if price_per_sqft is not None:
            valid_sales.append(row)
            price_per_sqft_values.append(price_per_sqft)

    if not price_per_sqft_values:
        print("No valid property records found.")
        return

    average_price_per_sqft = (
        sum(price_per_sqft_values) / len(price_per_sqft_values)
    )

    filtered_rows = []

    for row in valid_sales:
        price_per_sqft = calculate_price_per_sqft(row)

        if price_per_sqft < average_price_per_sqft:
            filtered_rows.append(row)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(filtered_rows)

    print(f"Average price per square foot: ${average_price_per_sqft:.2f}")
    print(f"Properties in input file: {len(rows)}")
    print(f"Properties written to output: {len(filtered_rows)}")
    print(f"Output file created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
