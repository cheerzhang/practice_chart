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

def compound_interest(start_date, baseline_start, days_number, r=0.005):
    Ds = []
    As = []
    Ps = []
    P = baseline_start  # 初始本金
    d = start_date  # 开始日期
    for i in range(days_number):
        # 计算复利
        A = P * (1 + r)
        # 输出结果
        if isinstance(d, pd.Timestamp):  # 如果 d 是 pd.Timestamp 类型，转换为 datetime
            d = d.to_pydatetime().date()  # 转换为日期对
        Ds.append(d)
        As.append(A)
        Ps.append(P)
        # 递增日期，确保跳过周末
        d += datetime.timedelta(days=1)
        while d.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            d += datetime.timedelta(days=1)
        # 更新本金为当前的 A
        P = A
    return Ds, As, Ps

def main():
    if "calculate" not in st.session_state:
        st.session_state.calculate = None
    df = load_data('./.local_db/main.csv')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    st.session_state.row = df
    # menu
    menu = ["Simulation", "Real", "Merge"]
    choice = st.sidebar.radio("Menu", menu)
    if choice == "Simulation":
        start_date = st.date_input("When's the start day?", datetime.date.today())
        start_date_ = np.datetime64(pd.to_datetime(start_date))
        if start_date_ not in df['date'].values:
            st.error('not fond')
        else:
            st.success('valid!')
            days_number = st.number_input("Insert a number", value=100, placeholder="Type a number...")
            r = st.number_input("Insert a number", value=0.005, placeholder="Type a number...")
            st.write(f'days: {days_number}, r: {r*100} %')
        # if valid
        if st.button('Calculate'):
            with st.spinner('Calculating...'):
                baseline_start = df[df['date'] == start_date_]['baseline'].values[0]
                r = 0.005
                Ds, As, Ps = compound_interest(start_date, baseline_start, days_number, r)
                data_df = pd.DataFrame(
                    {
                        'date': Ds,
                        'baseline': Ps,
                        'A_expect': As
                    }
                )
                data_df['precent_expect'] = r
                data_df['date'] = pd.to_datetime(data_df['date'], errors='coerce')
                st.session_state.calculate = data_df
            st.success('Calculated done!')
            st.bar_chart(data_df, x='date', y='baseline')
    if choice == 'Merge':
        st.header('Expected Table')
        df_new = st.session_state.calculate
        st.header('Currunt Table')
        df_row = st.session_state.row
        st.dataframe(df_row)
        if st.button('Merge'):
            st.write('...')
            df_ = df_new.merge(df_row, on='date', how='left')
            st.dataframe(df_)
    if choice == 'Real':
        st.bar_chart(df, x='date', y='baseline')




main()