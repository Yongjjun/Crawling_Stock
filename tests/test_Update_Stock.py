import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from matplotlib.ticker import FuncFormatter
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'

# 크롤링할 종목 리스트
stocks = {
    "삼성전자": "005930",
    "카카오": "035720",
    "네이버": "035420"
}

# 웹 드라이버 실행
options = webdriver.ChromeOptions()
# 창 숨기는 옵션 추가
options.add_argument("headless")
# driver 실행
driver = webdriver.Chrome(options=options)

# 각 종목 데이터를 저장할 리스트
dataframes = []

for stock_name, stock_code in stocks.items():
    base_url = f"https://finance.naver.com/item/sise_day.nhn?code={stock_code}&page="
    data = []

    # 10 페이지 크롤링
    for page in range(1, 10):
        url = base_url + str(page)
        driver.get(url)

        # 테이블 데이터 가져오기
        rows = driver.find_elements(By.CSS_SELECTOR, "table.type2 tr")

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) < 7:  # 데이터가 없는 행은 스킵
                continue

            date = cols[0].text.strip()
            close_price = cols[1].text.strip().replace(",", "")
            if date:
                data.append([date, close_price])

    df = pd.DataFrame(data, columns=["날짜", "종가"])
    df["종가"] = pd.to_numeric(df["종가"], errors='coerce')
    df.dropna(inplace=True)
    df["종목"] = stock_name  # 종목 이름 추가
    dataframes.append(df)

# 모든 종목 데이터 합치기
df_all = pd.concat(dataframes)

# 드라이버 종료
driver.quit()

# 날짜 컬럼 변환
df_all["날짜"] = pd.to_datetime(df_all["날짜"], errors='coerce')
df_all.dropna(subset=["날짜"], inplace=True)

df_all.sort_values(by="날짜", inplace=True)

# 하드코딩된 날짜 범위 설정 (CI/CD 환경에 맞게 날짜 자동 설정)
start_date = df_all["날짜"].min()  # 가장 초기 날짜
end_date = dt.datetime.today()  # 오늘 날짜

# 특정 기간 데이터 필터링
df_filtered = df_all[(df_all["날짜"] >= start_date) & (df_all["날짜"] <= end_date)]
print(f"✅ {start_date.date()} ~ {end_date.date()} 기간의 데이터만 조회합니다.")
print(df_filtered.head())  # 필터링된 데이터 확인

# 그래프 시각화
plt.figure(figsize=(10, 6))
for stock in df_filtered["종목"].unique():
    stock_df = df_filtered[df_filtered["종목"] == stock]
    plt.plot(stock_df["날짜"], stock_df["종가"], label=stock)

# y축에 정수만 표시하는 함수
def format_yaxis(x, pos):
    return f'{int(x):,}'  # 천 단위로 쉼표를 추가하여 정수로 표시

# x축 범위를 사용자 지정 날짜로 설정
plt.title("주식 종가 비교")
plt.xlabel("날짜")
plt.ylabel("종가 (원)")
plt.xticks(rotation=45)
plt.xlim(start_date, end_date)
plt.legend()
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))

# y축을 정수로 설정하고, 천 단위로 쉼표 표시
plt.gca().yaxis.set_major_formatter(FuncFormatter(format_yaxis))

plt.show()