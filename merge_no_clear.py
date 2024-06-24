import os
import pandas as pd
import re
import time

def sanitize_path(path):
    # 替换无效的文件名字符
    return re.sub(r'[<>:"/\\|?*]', '_', path)

def process_company_files(root_dir, company_name, keep_existing_merged_files):
    if not keep_existing_merged_files:
        backup_file_exists = os.path.exists(os.path.join(root_dir, f'{sanitize_path(company_name)}_merged_data.csv'))
        if backup_file_exists:
            print(f"{company_name} 的合并文件已存在，跳过合并")
            return pd.DataFrame()  # 返回空DataFrame

    company_data = pd.DataFrame()  # 用于存储单个子文件夹的数据
    for file in os.listdir(root_dir):
        file_path = os.path.join(root_dir, file)

        if file.endswith('.csv'):
            df = pd.read_csv(file_path,encoding='utf-8-sig')
            company_data = pd.concat([company_data, df], ignore_index=True)

    if not company_data.empty:
        company_data.drop_duplicates(subset=['title', 'Product Model'], keep='first', inplace=True)
        output_file = os.path.join(root_dir, f'{sanitize_path(company_name)}_merged_data.csv')
        try:
            company_data.to_csv(output_file, index=False,encoding='utf-8-sig')
            print(f"合并后的文件已保存到: {output_file}")
        except PermissionError:
            print(f"Permission denied: {output_file}")
            return company_data

        for file in os.listdir(root_dir):
            file_path = os.path.join(root_dir, file)
            if file.endswith('.csv') and file != f'{sanitize_path(company_name)}_merged_data.csv':
                try:
                    os.remove(file_path)
                except PermissionError:
                    print(f"Permission denied: {file_path}")

    return company_data

def merge_all_companies_data(all_data_list, all_companies_dir):
    if not all_data_list:
        print("没有数据可合并")
        return
    if all_data_list:
        start_time = time.time()
        all_data = pd.concat(all_data_list, ignore_index=True)
        all_companies_file = os.path.join(all_companies_dir, 'all_companies_merged_data.csv')
        os.makedirs(all_companies_dir, exist_ok=True)
        if os.path.exists(all_companies_file):
            try:
                existing_data = pd.read_csv(all_companies_file,encoding='utf-8-sig')
                all_data = pd.concat([existing_data, all_data], ignore_index=True)
                all_data.drop_duplicates(subset=['title', 'Product Model','company_name'], keep='last', inplace=True)
            except PermissionError:
                print(f"Permission denied: {all_companies_file}")
        else:
            all_data.drop_duplicates(subset=['title', 'Product Model'], keep='first', inplace=True)

        try:
            all_data.to_csv(all_companies_file, index=False,encoding='utf-8-sig')
            end_time = time.time()
            total_time = end_time - start_time
            print(f"所有公司合并文件已保存到: {all_companies_file}")
            print(f"总条数: {len(all_data)}")
            print(f"合并所有公司的时间: {total_time:.2f} seconds")
            print(f"平均每条数据的时间: {total_time / len(all_data):.2f} seconds")
        except PermissionError:
            print(f"Permission denied: {all_companies_file}")

def process_all_companies(root_dir, skip_existing_merged_files):
    all_data_list = []
    total_files = 0
    start_time = time.time()

    for subdir, dirs, files in os.walk(root_dir):
        if subdir == root_dir:
            continue  # 跳过根目录本身
        company_name = os.path.basename(subdir)
        company_data = process_company_files(subdir, company_name, skip_existing_merged_files)
        if not company_data.empty:
            all_data_list.append(company_data)
            total_files += len(company_data)

    end_time = time.time()
    total_time = end_time - start_time
    average_time = total_time / total_files if total_files else 0
    print(f"总文件数: {total_files}")
    print(f"处理所有文件的总时间: {total_time:.2f} seconds")
    print(f"平均每个文件的时间: {average_time:.2f} seconds")

    return all_data_list

if __name__ == "__main__":
    root_dir = "output_no_clear"  # 请替换为你的输入目录路径
    all_companies_dir = 'test_output'  # 请替换为保存所有公司合并文件的路径

    keep_existing_merged_files = True  # 是否保留现有的合并文件
    generate_all_companies_file = True  # 是否生成'all_companies_merged_data.csv'文件

    all_data_list = process_all_companies(root_dir, keep_existing_merged_files)

    if generate_all_companies_file:
        merge_all_companies_data(all_data_list, all_companies_dir)
