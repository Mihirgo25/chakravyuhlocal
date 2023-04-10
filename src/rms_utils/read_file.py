import csv, pdb

def read_file():
    with open(file='/Users/ssngurjar/ocean-rms/.data/free.csv') as file:
        input_file = csv.DictReader(file)
        headers = input_file.fieldnames
        total_lines = 0
        print(input_file.line_num)
        for row in input_file:
            if total_lines == 0:
                print(row)
            total_lines += 1
        print(input_file.line_num)
        file.seek(0)
        next(file)
        print(headers)
        new_total = 0
        for row in input_file:
            if new_total == 0:
                print(row)
            new_total = new_total + 1
        print(new_total, total_lines)