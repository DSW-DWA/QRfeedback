import csv

with open('new_info.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter='`')
    for row in reader:
        print(row)

with open('new_info.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter='`')
    processed_data = [(row[0], row[2]) for row in reader]


for row in processed_data:
    print(row)

with open('new_infoRefacted.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    for row in processed_data:
        writer.writerow(row)

print("Обработанные данные сохранены в файл 'обработанный_файл.csv'")
