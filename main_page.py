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

def summary_table(final_amount, invest_amount, total_cash):
    OneYearEarnt = final_amount-invest_amount
    OneYearEarntRate = OneYearEarnt / invest_amount
    OneYearEarntRate = round(OneYearEarntRate, 2)
    cash_onhands = round(total_cash, 2)
    summary_table_ = pd.DataFrame(
        {
            '3年后净值': [final_amount],
            '3年收益': [OneYearEarnt],
            '3年收益率': [OneYearEarntRate],
            '3年总提取': [cash_onhands]
        }
    )
    st.dataframe(summary_table_)
    return summary_table_

def one_time_invest_all(invest_amount_init, df_base):
    df = df_base[['日期','涨跌幅', '涨跌幅 %']].copy()
    df['当前净值'] = invest_amount_init  # 初始化第一天净值
    df['当天收益'] = 0 # 初始化当天收益
    df['当天提取'] = 0 # 初始化当天提取
    df['累计收益'] = 0 # 初始化累计收益
    for i in range(1, len(df)):
        # 计算当天收益 = 前一天当前净值 * 当天涨跌幅
        df.loc[i, '当天收益'] = df.loc[i - 1, '当前净值'] * df.loc[i, '涨跌幅']
        # 计算当前净值 = 前一天的当前净值 * (1 + 当天涨跌幅)
        df.loc[i, '当前净值'] = df.loc[i - 1, '当前净值'] * (1 + df.loc[i, '涨跌幅'])
    return df

def s2_invest_withdraw(invest_amount_init, withdraw_ratio, days, df_base):
    df = df_base[['日期','涨跌幅', '涨跌幅 %']].copy()
    df['当前净值'] = invest_amount_init  # 初始化第一天净值
    df['当天收益'] = 0 # 初始化当天收益
    df['当天提取'] = 0 # 初始化当天提取
    df['累计收益'] = 0 # 初始化累计收益
    EarntND = 0
    for i in range(1, len(df)):
        # 计算当天收益 = 前一天当前净值 * 当天涨跌幅
        df.loc[i, '当天收益'] = df.loc[i - 1, '当前净值'] * df.loc[i, '涨跌幅']
        # 累计N天收益
        if i % days != 0:
            EarntND = EarntND + df.loc[i, '当天收益']
            df.loc[i, '累计收益'] = EarntND
            # 计算是否提取收益
        else:
            if EarntND > 0:
                df.loc[i, '当天提取'] = EarntND * withdraw_ratio
                df.loc[i, '累计收益'] = EarntND
                EarntND = 0
        # 计算当天净值 = 前一天当前净值 + 当天收益 - 当天提取
        df.loc[i, '当前净值'] = df.loc[i - 1, '当前净值'] + df.loc[i, '当天收益'] - df.loc[i, '当天提取']
    return df




def main():
    df = load_data('./.local_db/main.csv')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df_base = load_data('./.local_db/ThreeYear500.csv')
    df_base['日期'] = pd.to_datetime(df_base['日期'], errors='coerce')
    df_base = df_base.sort_values('日期').reset_index(drop=True)
    df_base['涨跌幅 %'] = df_base['涨跌幅']
    df_base['涨跌幅'] = df_base['涨跌幅 %'].str.replace('%', '').astype(float) / 100
    
    # data
    invest_amount_init = 50000
    st.write("初始投资额", invest_amount_init)

    # menu
    menu = ["策略1", "策略2", "策略3", "策略4"]
    choice = st.sidebar.radio("Menu", menu)

    # 策略配置1
    if choice == '策略1':
        st.header('策略1:一次性投入')
        if invest_amount_init > 0:
            with st.spinner('calculating ...'):
                df_1 = one_time_invest_all(invest_amount_init, df_base)
                st.success('Calculated!')
                summary_table_ = summary_table(
                    final_amount = df_1.iloc[-1]['当前净值'], 
                    invest_amount = invest_amount_init,
                    total_cash = df_1['当天提取'].sum())
            st.dataframe(df_1[['日期','涨跌幅 %', '当前净值','当天收益','当天提取']])

    # 策略配置2
    if choice == "策略2":
        st.header('策略2: 一次性投入 + 每半年条件提取')
        withdraw_ratio_2 = st.select_slider("提取收益比率", options=[0.1, 0.2, 0.3, 0.4, 0.5],)
        if invest_amount_init > 0 and withdraw_ratio_2 >= 0.1:
            with st.spinner('calculating ...'):
                df_2 = s2_invest_withdraw(invest_amount_init, withdraw_ratio_2, 132, df_base)
                final_amount = df_2.iloc[-1]['当前净值']
                invest_amount = invest_amount_init
            with st.spinner('calculating ...'):
                total_cash = df_2['当天提取'].sum()
                st.success('Calculated.')
            summary_table_ = summary_table(
                final_amount = final_amount, 
                invest_amount = invest_amount,
                total_cash = total_cash)
            st.dataframe(df_2[['日期','涨跌幅 %', '当前净值','当天收益','当天提取', '累计收益']])

        start_date = st.date_input("When's the start day?", datetime.date.today())
        start_date_ = np.datetime64(pd.to_datetime(start_date))
    
    # 策略配置3
    if choice == '策略3':
        st.header('策略3: 一次性投入 + 每周条件提取')
        withdraw_ratio_3 = st.select_slider("提取收益比率", options=[0.1, 0.2, 0.3, 0.4, 0.5],)
        if invest_amount_init > 0 and withdraw_ratio_3 >= 0.1:
            with st.spinner('calculating ...'):
                df_3 = s2_invest_withdraw(invest_amount_init, withdraw_ratio_3, 5, df_base)
                final_amount = df_3.iloc[-1]['当前净值']
                invest_amount = invest_amount_init
            with st.spinner('calculating ...'):
                total_cash = df_3['当天提取'].sum()
                st.success('Calculated.')
            summary_table_ = summary_table(
                final_amount = final_amount, 
                invest_amount = invest_amount,
                total_cash = total_cash)
            st.dataframe(df_3[['日期','涨跌幅 %', '当前净值','当天收益','当天提取', '累计收益']])

    # 策略配置4
    if choice == "策略4":
        st.header('策略4:一次性投入 + 每月条件提取')
        withdraw_ratio_4 = st.select_slider("提取收益比率", options=[0.1, 0.2, 0.3, 0.4, 0.5],)
        if invest_amount_init > 0 and withdraw_ratio_4 >= 0.1:
            with st.spinner('calculating ...'):
                df_4 = s2_invest_withdraw(invest_amount_init, withdraw_ratio_4, 22, df_base)
                final_amount = df_4.iloc[-1]['当前净值']
                invest_amount = invest_amount_init
            with st.spinner('calculating ...'):
                total_cash = df_4['当天提取'].sum()
                st.success('Calculated.')
            summary_table_ = summary_table(
                final_amount = final_amount, 
                invest_amount = invest_amount,
                total_cash = total_cash)
            st.dataframe(df_4[['日期','涨跌幅 %', '当前净值','当天收益','当天提取', '累计收益']])

main()