import re


def find_missing_values(file, threshold_1, threshold_2):
    print(file)
    print(threshold_1)
    print(threshold_2)


while True:

    while True:
        filename = input("Please enter your file's name: ")
        if re.match(r"WindFarm[1-5].csv$|PvData.csv$", filename):
            # we're happy with the value given.
            # we're ready to exit the loop.
            break
        else:
            print("Sorry, your response does not match proper input! Please try again.")
            continue

    find_missing_values(filename, 5, 10)
