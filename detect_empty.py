import os

def find_immediate_folders_with_csv(root_directory):
    folders_with_csv = []

    for item in os.listdir(root_directory):
        item_path = os.path.join(root_directory, item)
        if os.path.isdir(item_path):
            if any(file.endswith('.csv') for file in os.listdir(item_path)):
                folders_with_csv.append(item)

    return folders_with_csv

def save_to_file(file_path, folders_with_csv):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("以下文件夹中包含CSV文件：\n")
        for folder in folders_with_csv:
            file.write(folder + '\n')
        file.write(f"\n总计文件夹数量：{len(folders_with_csv)}\n")

def main():
    root_directory = "input"  # 这里替换为你要遍历的根目录路径
    output_file = "清理之前不是空数据的.txt"  # 这里替换为你想保存结果的文件路径
    
    folders_with_csv = find_immediate_folders_with_csv(root_directory)

    print(f"总计文件夹数量：{len(folders_with_csv)}")
    
    if folders_with_csv:
        print("以下文件夹中包含CSV文件：")
        for folder in folders_with_csv:
            print(folder)
        save_to_file(output_file, folders_with_csv)
    else:
        print("所有文件夹中都不包含CSV文件。")
        with open(output_file, 'w', encoding='utf-8-sig') as file:
            file.write("所有文件夹中都不包含CSV文件。\n")

if __name__ == "__main__":
    main()
