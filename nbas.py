def process_data(data):
    print("Beginning data processing...")
    modified_data = data + " that has been modified"
    print("Data processing finished.")
    return modified_data


def main():
    data = "random data"
    print(data)
    modified_data = process_data(data)
    print(modified_data)


if __name__ == "__main__":
    main()
