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

def summary_table(final_amount, invest_amount, total_cash, withdraw_designed_days, withdraw_days):
    OneYearEarnt = final_amount-invest_amount
    OneYearEarntRate = OneYearEarnt / invest_amount
    OneYearEarntRate = round(OneYearEarntRate, 2)
    cash_onhands = round(total_cash, 2)
    withdraw_days_ratio = 0 if withdraw_days==0 else round(withdraw_days/withdraw_designed_days, 2)
    summary_table_ = pd.DataFrame(
        {
            '2年后净值': [final_amount],
            '2年收益': [OneYearEarnt],
            '2年收益率': [OneYearEarntRate],
            '2年总提取': [cash_onhands],
            '收益提取率: [提取次数/提取日]': [f'{withdraw_days} / {withdraw_designed_days}, {withdraw_days_ratio * 100} %']
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
    df['今日是否提取'] = False
    df['提取日'] = False
    for i in range(1, len(df)):
        # 计算当天收益 = 前一天当前净值 * 当天涨跌幅
        df.loc[i, '当天收益'] = df.loc[i - 1, '当前净值'] * df.loc[i, '涨跌幅']
        # 计算当前净值 = 前一天的当前净值 * (1 + 当天涨跌幅)
        df.loc[i, '当前净值'] = df.loc[i - 1, '当前净值'] * (1 + df.loc[i, '涨跌幅'])
    return df

def s2_invest_withdraw(invest_amount_init, withdraw_ratio, days, withdraw_limit, df_base):
    df = df_base[['日期','涨跌幅', '涨跌幅 %']].copy()
    df['当前净值'] = invest_amount_init  # 初始化第一天净值
    df['当天收益'] = 0 # 初始化当天收益
    df['当天提取'] = 0 # 初始化当天提取
    df['累计收益'] = 0 # 初始化累计收益
    df['今日是否提取'] = False
    df['提取日'] = False
    EarntND = 0
    for i in range(1, len(df)):
        # 计算当天收益 = 前一天当前净值 * 当天涨跌幅
        df.loc[i, '当天收益'] = df.loc[i - 1, '当前净值'] * df.loc[i, '涨跌幅']
        # 累计N天收益
        EarntND = EarntND + df.loc[i, '当天收益']
        df.loc[i, '累计收益'] = EarntND
        if i % days == 0:
            df.loc[i, '提取日'] = True
            if EarntND * withdraw_ratio >= withdraw_limit:
                df.loc[i, '当天提取'] = withdraw_limit
                df.loc[i, '今日是否提取'] = True
            EarntND = 0
        # 计算当天净值 = 前一天当前净值 + 当天收益 - 当天提取
        df.loc[i, '当前净值'] = df.loc[i - 1, '当前净值'] + df.loc[i, '当天收益'] - df.loc[i, '当天提取']
    return df




def main():
    df = load_data('./.local_db/main.csv')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df_ = load_data('./.local_db/TwoYear500.csv')
    df_['DATE'] = pd.to_datetime(df_['日期'], errors='coerce')
    df_ = df_.sort_values('DATE').reset_index(drop=True)
    df_['涨跌幅 %'] = df_['涨跌幅']
    df_['涨跌幅'] = df_['涨跌幅 %'].str.replace('%', '').astype(float) / 100

    # select the time range
    min_date = df_['DATE'].min()
    max_date = df_['DATE'].max()
    selected_date = st.date_input(
        "Select a date range", 
            (min_date, max_date),
            min_date,
            max_date,
            format='YYYY-MM-DD',
    )
    start_date = selected_date[0]
    start_date = pd.to_datetime(start_date)
    df_base = df_[df_['DATE']>=start_date]
    df_base = df_base.sort_values('DATE').reset_index(drop=True)
    features = ['日期','涨跌幅 %', '当前净值','当天收益','当天提取','今日是否提取','提取日']
    
    # data
    invest_amount_init = 40000
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
                    total_cash = df_1['当天提取'].sum(),
                    withdraw_designed_days = 0,
                    withdraw_days = 0)
            st.dataframe(df_1[features])

    # 策略配置2
    if choice == "策略2":
        st.header('策略2: 一次性投入 + 每半年条件提取')
        withraw_limit2 = 3000
        st.info(f'每半年收益提取上限 {withraw_limit2}')
        withdraw_ratio_2 = st.select_slider("提取收益比率", options=[0.1, 0.2, 0.3, 0.5, 0.9, 1.0],)
        if invest_amount_init > 0 and withdraw_ratio_2 >= 0.1:
            with st.spinner('calculating ...'):
                df_2 = s2_invest_withdraw(invest_amount_init, withdraw_ratio_2, 132, withraw_limit2, df_base)
                final_amount = df_2.iloc[-1]['当前净值']
                invest_amount = invest_amount_init
                withdraw_designed_days = df_2[df_2['提取日']==True].shape[0]
                withdraw_days = df_2[df_2['今日是否提取']==True].shape[0]
            with st.spinner('calculating ...'):
                total_cash = df_2['当天提取'].sum()
                st.success('Calculated.')
            summary_table_ = summary_table(
                final_amount = final_amount, 
                invest_amount = invest_amount,
                total_cash = total_cash,
                withdraw_designed_days = withdraw_designed_days,
                withdraw_days = withdraw_days)
            st.dataframe(df_2[features])

        start_date = st.date_input("When's the start day?", datetime.date.today())
        start_date_ = np.datetime64(pd.to_datetime(start_date))
    
    # 策略配置3
    if choice == '策略3':
        st.header('策略3: 一次性投入 + 每周条件提取')
        withraw_limit3 = 150
        st.info(f'每周收益提取上限 {withraw_limit3}')
        withdraw_ratio_3 = st.select_slider("提取收益比率", options=[0.1, 0.2, 0.3, 0.5, 0.9, 1.0],)
        if invest_amount_init > 0 and withdraw_ratio_3 >= 0.1:
            with st.spinner('calculating ...'):
                df_3 = s2_invest_withdraw(invest_amount_init, withdraw_ratio_3, 5, withraw_limit3, df_base)
                final_amount = df_3.iloc[-1]['当前净值']
                invest_amount = invest_amount_init
                withdraw_designed_days = df_3[df_3['提取日']==True].shape[0]
                withdraw_days = df_3[df_3['今日是否提取']==True].shape[0]
            with st.spinner('calculating ...'):
                total_cash = df_3['当天提取'].sum()
                st.success('Calculated.')
            summary_table_ = summary_table(
                final_amount = final_amount, 
                invest_amount = invest_amount,
                total_cash = total_cash,
                withdraw_designed_days = withdraw_designed_days,
                withdraw_days = withdraw_days)
            st.dataframe(df_3[features])

    # 策略配置4
    if choice == "策略4":
        st.header('策略4:一次性投入 + 每月条件提取')
        withraw_limit4 = 500
        st.info(f'每月收益提取上限 {withraw_limit4}')
        withdraw_ratio_4 = st.select_slider("提取收益比率", options=[0.1, 0.2, 0.3, 0.5, 0.9, 1.0],)
        if invest_amount_init > 0 and withdraw_ratio_4 >= 0.1:
            with st.spinner('calculating ...'):
                df_4 = s2_invest_withdraw(invest_amount_init, withdraw_ratio_4, 22, withraw_limit4, df_base)
                final_amount = df_4.iloc[-1]['当前净值']
                invest_amount = invest_amount_init
                withdraw_designed_days = df_4[df_4['提取日']==True].shape[0]
                withdraw_days = df_4[df_4['今日是否提取']==True].shape[0]
            with st.spinner('calculating ...'):
                total_cash = df_4['当天提取'].sum()
                st.success('Calculated.')
            summary_table_ = summary_table(
                final_amount = final_amount, 
                invest_amount = invest_amount,
                total_cash = total_cash,
                withdraw_designed_days = withdraw_designed_days,
                withdraw_days = withdraw_days)
            st.dataframe(df_4[features])

main()