import pandas as pd
import pymysql

# MySQL 연결 설정
connection = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='1234',
    database='bidres_items',
    charset='utf8mb4'
)

# CSV 파일 읽기 (utf-8-sig로 저장된 파일)
df = pd.read_csv('../bidResCategorizedUTF8SIG.csv', encoding='utf-8-sig')

# MySQL에 데이터 삽입
cursor = connection.cursor()

for index, row in df.iterrows():
    sql = """
    INSERT IGNORE INTO supply_classification (category, subcategory, items)
    VALUES (%s, %s, %s)
    """
    values = (row['구분'], row['세부 분류'], row['주요 품목'])
    cursor.execute(sql, values)

# 변경사항 커밋
connection.commit()

# 연결 종료
cursor.close()
connection.close()

print("데이터 삽입 완료!")