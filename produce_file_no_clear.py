import os
import re
import pandas as pd
import hashlib
import difflib
import time

# Function to generate a unique ID based on the content
def generate_unique_id(content):
    return int(hashlib.md5(content.encode()).hexdigest(), 16) % (10 ** 10)

def remove_lines_from_file(file_path, output_dir, skip_keywords_lines, root_directory):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    filtered_lines = []
    for line in lines:
        match = re.search(skip_keywords_lines, line.strip(), re.IGNORECASE)
        if match or re.match(r'^(产品|product|products)', line.strip(), re.IGNORECASE):
            matched_keyword = match.group() if match else '产品|product|products'
            print(f'Line to be deleted in {file_path}: {line.strip()}')
            print(f'Matched keyword: {matched_keyword}')
        else:
            filtered_lines.append(line)

    relative_path = os.path.relpath(file_path, root_directory)
    output_file_path = os.path.join(output_dir, relative_path)
    
    # Check if the directory exists and create it if not
    if not os.path.exists(os.path.dirname(output_file_path)):
        os.makedirs(os.path.dirname(output_file_path))

    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.writelines(filtered_lines)

    print(f'Processed file: {output_file_path}')

# Function to process all 'product_tree.txt' files in a directory structure
def process_directory(root_directory, output_directory, skip_keywords_lines):
    processed_directories = set()
    file_count = 0
    start_time = time.time()
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename == 'product_tree.txt' and dirpath not in processed_directories:
                file_path = os.path.join(dirpath, filename)
                remove_lines_from_file(file_path, output_directory, skip_keywords_lines, root_directory)
                processed_directories.add(dirpath)
                file_count += 1
    end_time = time.time()
    total_time = end_time - start_time
    average_time = total_time / file_count if file_count else 0
    return total_time, file_count, average_time

# Function to filter categories based on specified keywords and criteria
def filter_categories(categories, company_name, skip_keywords_categories):
    filtered = []
    url_pattern = re.compile(
        r'^(https?://)?([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}(/[a-zA-Z0-9\-\._~:/?#@!$&\'()*+,;=]*)?$'
    )
    for c in categories:
        c = c.strip()
        if re.search(skip_keywords_categories, c, re.IGNORECASE):
            continue
        if c.lower().startswith("产品") or re.match(r'^(product|products)', c, re.IGNORECASE):
            continue
        if c.lower() == company_name.lower() or c.lower() in company_name.lower():
            continue

        if url_pattern.match(c):
            continue
        filtered.append(c)
    return filtered

def filter_categories_name(categories, company_name, skip_keywords_categories):
    filtered = []
    chinese_char_pattern = re.compile(r'[\u4e00-\u9fff]')
    url_pattern = re.compile(
        r'^(https?://)?([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}(/[a-zA-Z0-9\-\._~:/?#@!$&\'()*+,;=]*)?$'
    )
    for c in categories:
        c = c.strip()
        if re.search(skip_keywords_categories, c, re.IGNORECASE):
            continue
        if c.lower().startswith("产品") or re.match(r'^(product|products)', c, re.IGNORECASE):
            continue
        if c.lower() == company_name.lower() or c.lower() in company_name.lower():
            continue
        
        similarity = difflib.SequenceMatcher(None, c.lower(), company_name.lower()).ratio()
        if similarity > 0.4:
            continue
        
        chinese_chars = chinese_char_pattern.findall(c)


        if len(chinese_chars) > 10:
            continue


        if url_pattern.match(c):
            continue
        filtered.append(c)
    
    return filtered

# Function to process each .csv file and convert to the desired structure
def process_csv_files(root_directory, output_directory, skip_keywords_categories):
    file_count = 0
    start_time = time.time()
    for dirpath, _, filenames in os.walk(root_directory):
        print(f'Processing directory: {dirpath}')
        relative_path = os.path.relpath(dirpath, root_directory)
        output_dir = os.path.join(output_directory, relative_path)
        
        # Check if the directory exists and create it if not
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for filename in filenames:
            print(f'Processing file: {filename}')
            if filename.endswith('.csv'):
                company_name = os.path.basename(dirpath)
                file_path = os.path.join(dirpath, filename)

                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                product_url, root_category_name, category_name, sub_category_name, detail_category_name = "无", "无", "无", "无", "无"
                root_category_id, category_id, sub_category_id, detail_category_id = 0, 0, 0, 0

                if lines and '|' in lines[0]:
                    lines = lines[1:]

                csv_data = {
                    "company_name": [],
                    "title": [],
                    "product_url": [],
                    "Product Model": [],
                    "base_info": [],
                    "root_category_name": [],
                    "root_category_id": [],
                    "category_name": [],
                    "category_id": [],
                    "sub_category_name": [],
                    "sub_category_id": [],
                    "detail_category_name": [],
                    "detail_category_id": []
                }

                for line in lines:
                    if line.startswith('产品网址：'):
                        product_url = line.split('：')[1].strip()
                    elif line.startswith('产品结构：'):
                        category_structure = re.split(r'->', line.split('：')[1].strip())
                        
                        filtered_categories = []
                        for category in category_structure:
                            parts = re.split(r'[|\-_]', category)
                            filtered_category_parts = filter_categories_name(parts, company_name, skip_keywords_categories)
                            if filtered_category_parts:
                                filtered_category = '|'.join(filtered_category_parts)
                                filtered_categories.append(filtered_category)
                        
                        if filtered_categories:
                            root_category_name = filtered_categories[0]
                            print(f'Root category name : {root_category_name}')
                            root_category_id = generate_unique_id(root_category_name)
                        if len(filtered_categories) > 1:
                            category_name = filtered_categories[1]
                            print(f'Category name: {category_name}')
                            category_id = generate_unique_id(category_name)
                        if len(filtered_categories) > 2:
                            sub_category_name = filtered_categories[2]
                            print(f'Sub-category name: {sub_category_name}')
                            sub_category_id = generate_unique_id(sub_category_name)
                        if len(filtered_categories) > 3:
                            detail_category_name = filtered_categories[3]
                            print(f'Detail category name: {detail_category_name}')
                            detail_category_id = generate_unique_id(detail_category_name)

                for line in lines:
                    if '|' in line and not line.startswith('|--'):
                        parts = line.split('|')
                        if parts is None:
                            continue
                        if len(parts) > 3:
                            title = parts[1].strip() if parts[1].strip() else "无"
                            product_model = parts[2].strip() if parts[2].strip() else "无"
                            base_info = parts[3].strip() if parts[3].strip() else "无"

                            csv_data["company_name"].append(company_name)
                            csv_data["title"].append(title)
                            csv_data["product_url"].append(product_url)
                            csv_data["Product Model"].append(product_model)
                            csv_data["base_info"].append(base_info)
                            csv_data["root_category_name"].append(root_category_name)
                            csv_data["root_category_id"].append(root_category_id)
                            csv_data["category_name"].append(category_name)
                            csv_data["category_id"].append(category_id)
                            csv_data["sub_category_name"].append(sub_category_name)
                            csv_data["sub_category_id"].append(sub_category_id)
                            csv_data["detail_category_name"].append(detail_category_name)
                            csv_data["detail_category_id"].append(detail_category_id)

                csv_df = pd.DataFrame(csv_data)
                csv_df = csv_df[csv_df["title"] != "产品名称"]

                output_csv_path = os.path.join(output_dir, filename)
                csv_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
                print(f'Processed file: {output_csv_path}')
                file_count += 1
    end_time = time.time()
    total_time = end_time - start_time
    average_time = total_time / file_count if file_count else 0
    return total_time, file_count, average_time

def main(root_directory, output_directory, skip_keywords_lines, skip_keywords_categories):
    csv_total_time, csv_file_count, csv_average_time = process_csv_files(root_directory, output_directory, skip_keywords_categories)

    txt_total_time, txt_file_count, txt_average_time = process_directory(root_directory, output_directory, skip_keywords_lines)

    print(f'Total CSV processing time: {csv_total_time:.2f} seconds')
    print(f'Total CSV files processed: {csv_file_count}')
    print(f'Average CSV time per file: {csv_average_time:.2f} seconds',end='\n\n')

    print(f'Total TXT processing time: {txt_total_time:.2f} seconds')
    print(f'Total TXT files processed: {txt_file_count}')
    print(f'Average TXT time per file: {txt_average_time:.2f} seconds',end='\n\n')

if __name__ == "__main__":
    root_directory = 'products'  # Change this to the actual directory path
    output_directory = 'output_no_clear'  # Change this to the desired output directory path

    skip_keywords_lines = (
        'dfghjkljhgfdsdfghjklkjhgfdsdfghj'
    )

    skip_keywords_categories = 'asdfghjkhgfdswqwertyui'


    main(root_directory, output_directory, skip_keywords_lines, skip_keywords_categories)
