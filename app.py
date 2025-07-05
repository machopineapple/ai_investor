
import streamlit as st
from ai_investing_tool_v5 import AIPortfolioManagerV5

st.title("AI Investing Assistant")

st.sidebar.header("Settings")
budget = st.sidebar.number_input("Initial Budget ($)", min_value=1000, value=10000, step=1000)
risk_profile = st.sidebar.selectbox("Risk Profile", ['conservative', 'moderate', 'aggressive'])

if 'manager' not in st.session_state:
    st.session_state.manager = None

if st.button("Create Portfolio"):
    st.session_state.manager = AIPortfolioManagerV5(budget=budget, risk_profile=risk_profile)
    st.session_state.manager.build_portfolio()
    st.success("Portfolio created!")

if st.session_state.manager:
    st.subheader("Current Portfolio Report")
    report = st.session_state.manager.report()
    for symbol, data in report.items():
        if symbol != 'Total Value' and symbol != 'Cash':
            st.write(f"{symbol}: {data['shares']} shares, Value: ${data['value']}")
    st.write(f"Cash: ${report['Cash']}")
    st.write(f"Total Portfolio Value: ${report['Total Value']}")

    if st.button("Rebalance Portfolio"):
        st.session_state.manager.rebalance()
        st.success("Portfolio rebalanced based on latest sentiment.")

    st.subheader("Holdings After Rebalancing")
    report = st.session_state.manager.report()
    for symbol, data in report.items():
        if symbol != 'Total Value' and symbol != 'Cash':
            st.write(f"{symbol}: {data['shares']} shares, Value: ${data['value']}")
    st.write(f"Cash: ${report['Cash']}")
    st.write(f"Total Portfolio Value: ${report['Total Value']}")
else:
    st.info("Create a portfolio to start investing.")
