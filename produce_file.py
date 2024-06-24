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
    root_directory = 'input'  # Change this to the actual directory path
    output_directory = 'output1'  # Change this to the desired output directory path

    skip_keywords_lines = (
        r'(新闻|亮相|祝贺|庆祝|资历|合作|伙伴|会谈|莅临|congratulations|celebration|news|contact|Solutions|获得专利分类导航|'
        r'仪式|研讨会|展览|展销会|贸易展|峰会|聚会|论坛|展示会|演示|主题演讲|演讲|开幕|发布会|现货供应|概述|新品|China产品Factory,产品Supplier|'
        r'公告|新闻稿|更新|披露|揭露|发布|展会|登录|qq|微信|微博|企业|核心产品|,,,,|'
        r'奖|荣誉|认可|表彰|奖项|嘉奖|展示|专注品质|匠心工艺|荣获|Location|央视CCTV|'
        r'社论|日记|报告|评论|总结|回顾|亮点|资讯|通知|消息|备忘录|通告|上市|博览会|资讯|动态|报道|奋斗|新时代|喜迎|关于我们|代表大会|喜讯)'
    )

    skip_keywords_categories = (
    r'('
    # General terms related to root or system-on-chip
    r'root|soc|'
    # Download-related keywords
    r'下载|'
    # Development board-related terms
    r'开发板|開發板|'
    # Company names and general tech terms
    r'凡科网|凡科網|肖邦|code|'
    # Home page and index-related terms
    r'首页|首頁|位置|'
    # Certifications and awards
    r'证书|證書|大会|大會|博览会|博覽會|展会|展會|功能描述|产品型号|產品型號|查询|查詢|官网|官網|加特兰微电子|加特蘭微電子|腾振科技|騰振科技|'
    # Company descriptions and FAQs
    r'公司简介|公司簡介|常见问题|常見問題|爱心元速|愛心元速|凡科网，让经营更简单|凡科網，讓經營更簡單|'
    # Specific award mention
    r'"PlusTechnologyforwinningthe""202116thChinaCoreFireEmergingProductAward""!!"|'
    # News and updates
    r'资讯|資訊|动态|動態|企业|企業|网页|網頁|网站|網站|荣誉|榮譽|恭喜|庆祝|慶祝|资质|資質|关于我们|關於我們|案例|精品展示|展示|'
    # Social media and contact terms
    r'qq|微博|'
    # Product center and new releases
    r'产品中心|產品中心|新品发布|新品發布|'
    # Location and navigation terms
    r'Location|loctions|所有查询|所有查詢|解决方案|解決方案|芯路通讯科技有限公司|芯路通訊科技有限公司|二维码|二維碼|'
    # Marketing and promotional phrases
    r'new|congratulations|celebration|news|home|index|about|contact|location|新闻|新聞|祝贺|祝賀|'
    # Detailed product information
    r'详细信息|詳細信息|专注品质|專注品質|匠心工艺|匠心工藝|更自由|登录|登錄|查询查询|查詢查詢|华大电子|華大電子|China产品Factory,產品Supplier|获得|獲得|'
    # Product descriptions and lists
    r'产品中心|產品中心|产品展示|產品展示|产品介绍|產品介紹|产品列表|產品列表|产品目录|產品目錄|产品详情|產品詳情|产品系列|產品系列|产品型号|產品型號|产品规格|產品規格|'
    r'产品特点|產品特點|产品优势|產品優勢|产品功能|產品功能|产品参数|產品參數|产品图片|產品圖片|产品信息|產品信息|产品说明|產品說明|产品分类|產品分類|产品报价|產品報價|'
    r'产品价格|產品價格|产品销售|產品銷售|产品定制|產品定製|产品定位|產品定位|产品定价质量|產品定價質量|Kewell|Rising华兴|Rising華興|新品发布|新品發布|业务说明|業務說明|震撼发布|震撼發布|'
    # Homepage and promotion terms
    r'首頁|讓控制更簡單|ChinaProductsFactory,ProductsSupplier|language|'
    # File extensions
    r'.pdf|.doc|.docx|.xls|.xlsx|.ppt|.pptx|.txt|.zip|.rar|en\|us|(?i)slid\d+|'
    # Marketing and product descriptions
    r'获得专利分类导航|獲得專利分類導航|现货供应|現貨供應|概述|新品|先科|(?i)part\d+|新时代|新時代|美思迪赛|美思迪賽|全部产品|全部產品|又一个|又一個|'
    r'核心产品|核心產品|,,,,|芯导|芯導|恭贺|恭賀|引领|引領|深爱|深愛|Xrany元霓|'
    r'应用领域|應用領域|全系统解决方案|全系統解決方案|召开|召開|公司能力|行业解决方案|行業解決方案|KWansemi冠禹|'
    # Company details and partnerships
    r'资历|資歷|合作|伙伴|會談|莅临|蒞臨|'
    # Company abbreviations and titles
    r'Inc\.|Corp\.|Ltd\.|LLC|PLC|Co\.|GmbH|'
    # News and company product details
    r'报道|報導|介绍|介紹|公司产品|公司產品|Yourlocation|招聘|薪酬|人才|招贤纳士|招賢納士|喜讯|喜訊|荣获|榮獲|算法科学家|算法科學家|十年沉淀，六代匠心|十年沉澱，六代匠心|极昼系列的“前世今生”|極昼系列的“前世今生”|'
    # Generic phrases and sample code mentions
    r'更多|示例代码|示例代碼|了解|热爱|熱愛|激情|展示|精彩|便捷|下载中心|下載中心|列表|第(?:[0-9一二三四五六七八九十百千万]+)页|第(?:[0-9一二三四五六七八九十百萬]+)頁|'
    r'信昌|国科微|國科微|信浦|质量|質量|Kewell|更简单|更簡單|code|示例|zip.|使用说明|使用說明|国科微|國科微|信浦|七月上海|'
    # Welcome messages and company mentions
    r'Welcometowww.simgui.com.cn|TiandyTechnologies|取件码|取件碼|媒体中心|媒體中心|百强|百強|伟肯vacon，VACON代理，莱姆传感器|偉肯vacon，VACON代理，萊姆傳感器|'
    # Navigation and pagination terms
    r'下一页|下一頁|继往开来|繼往開來|爱科研|愛科研|Company|Exhibitioninvitation|website|'
    # No results found and common result count patterns
    r'未找到|相应参数|相應參數|共\d+条|共\d+條|共\d+页|共\d+頁|共\d+个|共\d+個|共\d+款|共\d+種|共\d+家|共\d+篇|共\d+条记录|共\d+條記錄|共\d+个结果|共\d+個結果|'
    r'共\d+个产品|共\d+個產品|共\d+个项目|共\d+個項目|共\d+个新闻|共\d+個新聞|共\d+个案例|共\d+個案例|共\d+个活动|共\d+個活動|共\d+个专题|共\d+個專題|'
    # Company-related terms and details
    r'芯片公司|芯片公司|Wuxii|Company|查看详情|查看詳情'
    r')'
)


    main(root_directory, output_directory, skip_keywords_lines, skip_keywords_categories)
