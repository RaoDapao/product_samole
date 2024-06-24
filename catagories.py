import csv

def extract_unique_values(file_path, key):
    unique_values = set()
    
    with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if key in row:
                unique_values.add(row[key])
    
    return unique_values

def save_unique_values(file_path, unique_values):
    with open(file_path, mode='w', encoding='utf-8-sig', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Unique Values'])  # 写入表头
        for value in unique_values:
            writer.writerow([value])
            print(f'Unique value: {value}')


input_file_path = r'output2\all_companies_merged_data.csv'  # 替换为你的CSV文件路径
output_file_path = 'unique_catagories.csv'  # 替换为你想要保存的CSV文件路径
key = 'root_category_name'  # 替换为你想要提取的键

unique_values = extract_unique_values(input_file_path, key)
save_unique_values(output_file_path, unique_values)
