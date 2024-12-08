import streamlit as st
import pandas as pd
import numpy as np
import os, datetime



def load_data(csv_name):
    if os.path.exists(csv_name):
        df = pd.read_csv(csv_name)
    else:
        df = None
    return df

def summary_table(final_amount, invest_amount):
    OneYearEarnt = (final_amount-invest_amount)
    OneYearEarntRate = OneYearEarnt / invest_amount
    summary_table = pd.DataFrame(
        {
            '1年后净值': [final_amount],
            '1年收益': [OneYearEarnt],
            '1年收益率': [round(OneYearEarntRate, 2)]
        }
    )
    st.dataframe(summary_table)

def one_time_invest_all(invest_amount_init, df_base):
    df = df_base[['日期','涨跌幅', '涨跌幅 %']].copy()
    df['当前净值'] = invest_amount_init  # 初始化第一天净值
    df['当天收益'] = 0 # 初始化当天收益
    for i in range(1, len(df)):
        # 计算当天收益 = 前一天当前净值 * 当天涨跌幅
        df.loc[i, '当天收益'] = df.loc[i - 1, '当前净值'] * df.loc[i, '涨跌幅']
        # 计算当前净值 = 前一天的当前净值 * (1 + 当天涨跌幅)
        df.loc[i, '当前净值'] = df.loc[i - 1, '当前净值'] * (1 + df.loc[i, '涨跌幅'])
    return df

def invest_withdraw(invest_amount_init, withdraw_ratio,df_base):
    df = df_base[['日期','涨跌幅', '涨跌幅 %']].copy()
    df['当前净值'] = invest_amount_init  # 初始化第一天净值
    df['当天收益'] = 0 # 初始化当天收益
    df['当天提取'] = 0 # 初始化当天提取
    for i in range(1, len(df)):
        # 计算当天收益 = 前一天当前净值 * 当天涨跌幅
        df.loc[i, '当天收益'] = df.loc[i - 1, '当前净值'] * df.loc[i, '涨跌幅']
        # 计算是否提取收益
        if df.loc[i, '涨跌幅'] > 0:
            df.loc[i, '当天提取'] = df.loc[i, '当天收益'] * withdraw_ratio
        # 计算当天净值 = 前一天当前净值 + 当天收益 - 当天提取
        df.loc[i, '当前净值'] = df.loc[i - 1, '当前净值'] + df.loc[i, '当天收益'] - df.loc[i, '当天提取']
    return df





def main():
    df = load_data('./.local_db/main.csv')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df_base = load_data('./.local_db/OneYear500.csv')
    df_base['日期'] = pd.to_datetime(df_base['日期'], errors='coerce')
    df_base = df_base.sort_values('日期').reset_index(drop=True)
    df_base['涨跌幅 %'] = df_base['涨跌幅']
    df_base['涨跌幅'] = df_base['涨跌幅 %'].str.replace('%', '').astype(float) / 100
    
    # data
    invest_amount_init = 40000
    st.write("初始投资额", invest_amount_init)

    # menu
    menu = ["策略1", "策略2", "2"]
    choice = st.sidebar.radio("Menu", menu)

    # 策略配置1
    if choice == '策略1':
        st.header('策略1:一次性投入')
        if invest_amount_init > 0:
            df_1 = one_time_invest_all(invest_amount_init, df_base)
            summary_table(
                final_amount = df_1.iloc[-1]['当前净值'], 
                invest_amount = invest_amount_init)
            st.dataframe(df_1[['日期','涨跌幅 %', '当前净值','当天收益']])

    # 策略配置2
    if choice == "策略2":
        st.header('策略2:一次性投入 + 定期提取')
        withdraw_ratio = st.select_slider("提取收益比率",
            options=[0.1, 0.2, 0.3, 0.4, 0.5],)
        if invest_amount_init > 0:
            df_2 = invest_withdraw(invest_amount_init, 
                                   withdraw_ratio,
                                   df_base)
            summary_table(
                final_amount = df_2.iloc[-1]['当前净值'], 
                invest_amount = invest_amount_init)
            st.dataframe(df_2[['日期','涨跌幅 %', '当前净值','当天收益','当天提取']])


        start_date = st.date_input("When's the start day?", datetime.date.today())
        start_date_ = np.datetime64(pd.to_datetime(start_date))
    if choice == '2':
        st.header('Expected Table')
    




main()