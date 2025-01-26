import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.stats.api as sms
import requests
import pandas as pd
import datetime
import openpyxl
import calendar
import matplotlib.pyplot as plt
import seaborn
from bs4 import BeautifulSoup
import random

# URL для получения ключевой ставки
url = f"https://base.garant.ru/10180094/"

# Запрос данных
response = requests.get(url)
page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")

alls16 = soup.findAll('p', class_='s_16')
alls1 = soup.findAll('p', class_='s_1')

# -------------s16
for j in range(len(alls16)):
    new_date = []
    date = str(alls16[j])
    for i in range(len(date)):
        if date[i] == '>':
            new_date = date[i + 1:]
            break
    for i in range(len(new_date)):
        if new_date[i] == '<':
            new_date = new_date[:i]
            break
    alls16[j] = new_date
alls16 = alls16[2:]
for i in range(1, len(alls16) // 2):
    alls16.pop(i)
alls16 = alls16[:54]
alls16 = alls16[1:]

for j in range(len(alls16)):
    split_str_date = str(alls16[j]).split(' ')
    months_rus = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября',
                  'ноября', 'декабря']
    for el in split_str_date:
        if 1105 > ord(el[0]) > 1040:
            for i in range(len(months_rus)):
                if months_rus[i] == el:
                    el = str(i + 1)
                    if len(el) == 1:
                        el = '0' + el
                    split_str_date = [(el if x == months_rus[i] else x) for x in split_str_date]
    alls16[j] = ''
    for el in split_str_date:
        alls16[j] += el + ' '

# ---------------s1
for j in range(len(alls1)):
    new_key = []
    str_of_Key = str(alls1[j])
    for i in range(len(str_of_Key)):
        if str_of_Key[i] == '>':
            new_key = str_of_Key[i + 1:]
            break
    for i in range(len(new_key)):
        if new_key[i] == '<':
            new_key = new_key[:i]
            break
    alls1[j] = new_key

alls1 = alls1[1:]


def key_period_of_dates_to_datetime(alls16, alls1):
    KeyRate = []
    DateOfKeyRate = []
    for i in range(len(alls16)):
        list_of_dates = str(alls16[i]).split('- ')
        first_date = (datetime.datetime.strptime(list_of_dates[0], "%d %m %Y г. ")).date()
        second_date = (datetime.datetime.strptime(list_of_dates[1], "%d %m %Y г. ")).date()
        numdays = first_date - second_date
        DateOfKeyRate += [second_date - datetime.timedelta(days=x) for x in range(-int(numdays.days))] + [first_date]
        KeyRate += [alls1[i] for k in range(-int(numdays.days) + 1)]
    for i in range(len(KeyRate)):
        str1 = KeyRate[i]
        split = str1.split(',')
        KeyRate[i] = int(split[0]) + int(split[1]) / 100
    DateOfKeyRate.reverse()
    KeyRate.reverse()
    return DateOfKeyRate, KeyRate


# ----------------средние ставки по ипотекам в россии
data_file = 'sred.xlsx'
sheet = openpyxl.load_workbook(data_file)
ws = sheet['Worksheet']
all_rows = list(ws.rows)


# sex
def percent_of_some_avarage_rate(all_rows, num_of_row):
    date_ip = []
    per_ip = []
    for row in all_rows[8:77]:
        date_ip.append(row[0].value)
        per_ip.append(row[num_of_row].value)
    return date_ip, per_ip


def percent_period_of_dates_to_datetime(date_ip, per_ip):
    DateOfPerIp = []
    PerIp = []
    for i in range(len(date_ip)):
        date_ip[i] = datetime.datetime.strptime(str(date_ip[i]), "%d.%m.%Y")
        numdays = calendar.monthrange(date_ip[i].year, date_ip[i].month)[1]
        DateOfPerIp += [datetime.date(date_ip[i].year, date_ip[i].month, x) for x in range(1, numdays + 1)]
        PerIp += [per_ip[i] for _ in range(int(numdays))]
    return DateOfPerIp, PerIp


# ----------- Приводим данные к послед исслед
def make_two_lists_the_same(DateOfPerIp, PerIp, DateOfKeyRate, KeyRate):
    min_date = max(DateOfPerIp[0], DateOfKeyRate[0])
    # print(min_date, DateOfPerIp[0], DateOfKeyRate[0])
    # print(max_date, DateOfPerIp[-1], DateOfKeyRate[-1])
    min_index_per = DateOfPerIp.index(min_date)
    min_index_key = DateOfKeyRate.index(min_date)
    if min_index_key > min_index_per:
        DateOfKeyRate = DateOfKeyRate[min_index_key:]
        KeyRate = KeyRate[min_index_key:]
    else:
        DateOfPerIp = DateOfPerIp[min_index_per:]
        PerIp = PerIp[min_index_per:]
    min_len = min(len(DateOfKeyRate), len(DateOfPerIp))
    DateOfKeyRate = DateOfKeyRate[:min_len]
    DateOfPerIp = DateOfPerIp[:min_len]
    KeyRate = KeyRate[:min_len]
    PerIp = PerIp[:min_len]
    return DateOfPerIp, PerIp, DateOfKeyRate, KeyRate


DateOfKeyRate, KeyRate = key_period_of_dates_to_datetime(alls16, alls1)
# Numm1 = 0
# Numm2 = 2000
# KeyRate = KeyRate[Numm1:Numm2]
# PerIp = PerIp[Numm1:Numm2]
DateOfPerIp, PerIp, DateOfKeyRate, KeyRate = make_two_lists_the_same(DateOfPerIp=(
    percent_period_of_dates_to_datetime(date_ip=percent_of_some_avarage_rate(all_rows=all_rows, num_of_row=1)[0],
                                        per_ip=percent_of_some_avarage_rate(all_rows=all_rows, num_of_row=1)[1]))[0],
                                                                     PerIp=(percent_period_of_dates_to_datetime(date_ip=
                                                                                                                percent_of_some_avarage_rate(
                                                                                                                    all_rows=all_rows,
                                                                                                                    num_of_row=1)[
                                                                                                                    0],
                                                                                                                per_ip=
                                                                                                                percent_of_some_avarage_rate(
                                                                                                                    all_rows=all_rows,
                                                                                                                    num_of_row=1)[
                                                                                                                    1]))[
                                                                         1],
                                                                     DateOfKeyRate=DateOfKeyRate, KeyRate=KeyRate)
plt.xlabel('Год')
plt.subplot(2, 3, 1)
df = {'Ключевая ставка': KeyRate,
      'Ставка по ипотеке': PerIp}
seaborn.scatterplot(x=df['Ключевая ставка'], y=df['Ставка по ипотеке'])
plt.subplot(2, 3, 4)
seaborn.lineplot(x=DateOfKeyRate, y=df['Ключевая ставка'])
seaborn.lineplot(x=DateOfPerIp, y=df['Ставка по ипотеке'])
DateOfPerIp, PerIp, DateOfKeyRate, KeyRate = make_two_lists_the_same(DateOfPerIp=(
    percent_period_of_dates_to_datetime(date_ip=percent_of_some_avarage_rate(all_rows=all_rows, num_of_row=2)[0],
                                        per_ip=percent_of_some_avarage_rate(all_rows=all_rows, num_of_row=2)[1]))[0],
                                                                     PerIp=(percent_period_of_dates_to_datetime(date_ip=
                                                                                                                percent_of_some_avarage_rate(
                                                                                                                    all_rows=all_rows,
                                                                                                                    num_of_row=2)[
                                                                                                                    0],
                                                                                                                per_ip=
                                                                                                                percent_of_some_avarage_rate(
                                                                                                                    all_rows=all_rows,
                                                                                                                    num_of_row=2)[
                                                                                                                    1]))[
                                                                         1],
                                                                     DateOfKeyRate=DateOfKeyRate, KeyRate=KeyRate)
plt.ylabel('В процентах')
plt.xlabel('Год')
plt.subplot(2, 3, 2)
df = {'Ключевая ставка': KeyRate,
      'Ставка по ипотеке': PerIp}
seaborn.scatterplot(x=df['Ключевая ставка'], y=df['Ставка по ипотеке'])
plt.subplot(2, 3, 5)
seaborn.lineplot(x=DateOfKeyRate, y=df['Ключевая ставка'])
seaborn.lineplot(x=DateOfPerIp, y=df['Ставка по ипотеке'])
DateOfPerIp, PerIp, DateOfKeyRate, KeyRate = make_two_lists_the_same(DateOfPerIp=(
    percent_period_of_dates_to_datetime(date_ip=percent_of_some_avarage_rate(all_rows=all_rows, num_of_row=3)[0],
                                        per_ip=percent_of_some_avarage_rate(all_rows=all_rows, num_of_row=3)[1]))[0],
                                                                     PerIp=(percent_period_of_dates_to_datetime(date_ip=
                                                                                                                percent_of_some_avarage_rate(
                                                                                                                    all_rows=all_rows,
                                                                                                                    num_of_row=3)[
                                                                                                                    0],
                                                                                                                per_ip=
                                                                                                                percent_of_some_avarage_rate(
                                                                                                                    all_rows=all_rows,
                                                                                                                    num_of_row=3)[
                                                                                                                    1]))[
                                                                         1],
                                                                     DateOfKeyRate=DateOfKeyRate, KeyRate=KeyRate)
plt.ylabel('В процентах')
plt.xlabel('Год')
plt.subplot(2, 3, 3)
df = {'Ключевая ставка': KeyRate,
      'Ставка по ипотеке': PerIp}
seaborn.scatterplot(x=df['Ключевая ставка'], y=df['Ставка по ипотеке'])
plt.subplot(2, 3, 6)
seaborn.lineplot(x=DateOfKeyRate, y=df['Ключевая ставка'])
seaborn.lineplot(x=DateOfPerIp, y=df['Ставка по ипотеке'])
plt.ylabel('В процентах')
plt.xlabel('Год')
plt.show()

# ----------------- 1. Вычисление коэффициента корреляции (Пирсона) ----------------
rng = np.random.default_rng()
method = stats.PermutationMethod(random_state=rng)
correlation, p_value = stats.pearsonr(KeyRate, PerIp)
print(f'Коэффициент корреляции Пирсона: {correlation:.4f}, p-значение: {p_value:.4f}')

# ----------------- 2. Тест Уайта на гетероскедастичность ----------------
# Добавим константу для модели (это эквивалентно добавлению столбца единиц в регрессионную модель)
X = sm.add_constant(KeyRate)
model = sm.OLS(PerIp, X).fit()
residuals = model.resid  # Получаем остатки модели
white_test = sms.het_white(residuals, model.model.exog)  # Тест Уайта на гетероскедастичность
print(f'Результаты теста Уайта на гетероскедастичность: {white_test}')

# ----------------- 3. Доверительный интервал при alpha = 0.9 ----------------
print(stats.pearsonr(KeyRate, PerIp).confidence_interval(confidence_level=0.9))

# ----------------- Визуализация ----------------
plt.figure(figsize=(14, 8))
plt.subplot(2, 1, 1)
seaborn.scatterplot(x=KeyRate, y=PerIp)
plt.title('Ключевая ставка vs Ставка по ипотеке')

plt.subplot(2, 1, 2)
seaborn.lineplot(x=DateOfKeyRate, y=KeyRate, label='Ключевая ставка')
seaborn.lineplot(x=DateOfPerIp, y=PerIp, label='Ставка по ипотеке')
plt.title('Ключевая ставка и Ставка по ипотеке')

plt.tight_layout()
plt.show()
