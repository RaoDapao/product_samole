import os
import re

def delete_matching_csv_files(root_directory,key_words):
    # Define the keywords to match in the filenames


    # Walk through the directory
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            
            # Check if the file is a .csv
            if filename.endswith('.csv'):
                # Check if the filename matches any of the keywords
                match = re.search(keywords, filename, re.IGNORECASE)
                if match:
                    try:
                        os.remove(file_path)
                        print(f'Deleted file: {file_path}')
                        print(f'Matched keyword: {match.group()}')
                    except Exception as e:
                        print(f'Error deleting file {file_path}: {e}')




if __name__ == '__main__':
    # Define the root directory
    root_directory = 'input'  # Change this to the actual directory path
    keywords = (
        r'(新闻|亮相|祝贺|庆祝|资历|合作|伙伴|会谈|莅临|congratulations|celebration|news|home|contact|登录|qq|微博|'
        r'仪式|研讨会|展览|展销会|贸易展|峰会|聚会|大会|论坛|展示会|演示|主题演讲|演讲|开幕|发布会|'
        r'公告|新闻稿|更新|披露|揭露|发布|专注品质|匠心工艺|更自由|登录|企业名称|联系我们|'
        r'奖|荣誉|认可|表彰|奖项|嘉奖|日志|招聘|薪酬|人才|招贤纳士|喜讯|算法科学家|网站首页|'
        r'社论|日记|报告|评论|总结|回顾|亮点|资讯|通知|消息|通告|上市|开工|大会|更多|展会|了解|精彩|热爱|动态|报道|奋斗|新时代|喜迎|关于我们|代表大会)'
    )
    # Delete matching .csv files
    delete_matching_csv_files(root_directory, keywords)

