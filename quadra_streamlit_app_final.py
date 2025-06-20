
import streamlit as st

# Константы по стратегиям
strategies = {
    'LRI': {'gold': 0.50, 'flip': 0.50, 'algo': 0.00},
    'MRI': {'gold': 0.30, 'flip': 0.30, 'algo': 0.40},
    'HRI': {'gold': 0.20, 'flip': 0.10, 'algo': 0.70},
}

# Фиксированные комиссии
QUADRA_MGMT_FEE = 0.02
QUADRA_PERF_FEE = 0.20
THIRD_MGMT_FEE = 0.02
THIRD_PERF_FEE = 0.30

def gold_arbitrage(investment, months, monthly_return):
    active_months = min(9, months)
    gross = investment * ((1 + monthly_return) ** active_months - 1)
    fee = gross * QUADRA_PERF_FEE
    return gross - fee, fee

def flipping(investment, months, return_per_6m):
    periods = months // 6
    gross = investment * return_per_6m * periods
    fee = gross * QUADRA_PERF_FEE
    return gross - fee, fee

def algo_trading(investment, months, annual_return):
    gross = investment * (annual_return * months / 12)
    third_fee = gross * THIRD_PERF_FEE
    net_after = gross - third_fee
    quadra_fee = net_after * QUADRA_PERF_FEE
    return net_after - quadra_fee, quadra_fee, third_fee

st.title("💼 Quadra Investment Platform")

menu = st.sidebar.selectbox(
    "Выберите калькулятор:",
    ("📘 Мульти-стратегии", "🎯 Подбор стратегии под цель", "🔧 Кастомный калькулятор")
)

amount = st.number_input("Сумма инвестиции ($):", key="amount_input", min_value=1000.0, step=1000.0)
months = st.number_input("Срок инвестирования (мес):", key="months_input", min_value=6, step=1)

if menu == "📘 Мульти-стратегии":
    g_monthly = st.number_input("Gold доходность (% в мес):", min_value=0.0, step=0.1) / 100
    f_6m = st.number_input("Flipping доходность (% за 6 мес):", min_value=0.0, step=0.1) / 100
    a_annual = st.number_input("Algo доходность (% в год):", min_value=0.0, step=0.1) / 100

    for name, mix in strategies.items():
        g_amt = amount * mix['gold']
        f_amt = amount * mix['flip']
        a_amt = amount * mix['algo']

        g_inv, g_fee = gold_arbitrage(g_amt, months, g_monthly) if g_amt > 0 else (0, 0)
        f_inv, f_fee = flipping(f_amt, months, f_6m) if f_amt > 0 else (0, 0)
        a_inv, a_fee, third_fee = algo_trading(a_amt, months, a_annual) if a_amt > 0 else (0, 0, 0)

        quadra_mgmt = amount * QUADRA_MGMT_FEE
        third_mgmt = a_amt * THIRD_MGMT_FEE

        investor_profit = g_inv + f_inv + a_inv - quadra_mgmt - third_mgmt
        quadra_profit = g_fee + f_fee + a_fee + quadra_mgmt
        third_profit = third_fee + third_mgmt

        st.subheader(f"🔹 Стратегия: {name}")
        st.write(f"**Инвестор:** ${investor_profit:,.2f} ({investor_profit / amount * 100:.2f}%)")
        st.write(f"**Quadra:** ${quadra_profit:,.2f} ({quadra_profit / amount * 100:.2f}%)")
        st.write(f"**Сторонний подрядчик:** ${third_profit:,.2f} ({third_profit / amount * 100:.2f}%)")

elif menu == "🎯 Подбор стратегии под цель":
    target_return = st.number_input("Желаемая доходность инвестора (%):", key="target_return_input", min_value=0.0, step=0.1) / 100
    max_gold_monthly = 0.08
    max_flip_6m = 0.18
    max_algo_annual = 1.20
    step = 0.01

    if st.button("🔍 Посчитать"):
        found = False
        for name, mix in strategies.items():
            g_weight = mix['gold']
            f_weight = mix['flip']
            a_weight = mix['algo']

            g_amt = amount * g_weight
            f_amt = amount * f_weight
            a_amt = amount * a_weight

            g_ret = max_gold_monthly
            f_ret = max_flip_6m
            a_ret = 0.00
            while a_ret <= max_algo_annual:
                g_inv, _ = gold_arbitrage(g_amt, months, g_ret) if g_amt > 0 else (0, 0)
                f_inv, _ = flipping(f_amt, months, f_ret) if f_amt > 0 else (0, 0)
                a_inv, _, _ = algo_trading(a_amt, months, a_ret) if a_amt > 0 else (0, 0, 0)

                mgmt_quadra = amount * QUADRA_MGMT_FEE
                mgmt_third = a_amt * THIRD_MGMT_FEE

                total_profit = g_inv + f_inv + a_inv - mgmt_quadra - mgmt_third
                investor_yield = total_profit / amount

                if investor_yield >= target_return:
                    st.success(f"✅ Подходящая стратегия: {name}")
                    st.write(f"Gold доходность: {g_ret * 100:.2f}%/мес")
                    st.write(f"Flip доходность: {f_ret * 100:.2f}%/6 мес")
                    st.write(f"Algo доходность: {a_ret * 100:.2f}%/год")
                    st.write(f"💡 Quadra: ${(g_inv + f_inv + a_inv) * QUADRA_PERF_FEE + mgmt_quadra:,.2f}")
                    st.write(f"💡 Подрядчик: ${(a_amt * a_ret * months / 12) * THIRD_PERF_FEE + mgmt_third:,.2f}")
                    found = True
                    break
                a_ret += step
            if found:
                break
        if not found:
            st.error("❌ Не удалось достичь цели даже с максимальными параметрами.")

    target_return = st.number_input("Желаемая доходность инвестора (%):", key="target_return_input", min_value=0.0, step=0.1) / 100
    max_gold_monthly = 0.08
    max_flip_6m = 0.18
    max_algo_annual = 1.20
    step = 0.01
    found = False

    for name, mix in strategies.items():
        g_weight = mix['gold']
        f_weight = mix['flip']
        a_weight = mix['algo']

        g_amt = amount * g_weight
        f_amt = amount * f_weight
        a_amt = amount * a_weight

        g_ret = max_gold_monthly
        f_ret = max_flip_6m
        a_ret = 0.00
        while a_ret <= max_algo_annual:
            g_inv, _ = gold_arbitrage(g_amt, months, g_ret) if g_amt > 0 else (0, 0)
            f_inv, _ = flipping(f_amt, months, f_ret) if f_amt > 0 else (0, 0)
            a_inv, _, _ = algo_trading(a_amt, months, a_ret) if a_amt > 0 else (0, 0, 0)

            mgmt_quadra = amount * QUADRA_MGMT_FEE
            mgmt_third = a_amt * THIRD_MGMT_FEE

            total_profit = g_inv + f_inv + a_inv - mgmt_quadra - mgmt_third
            investor_yield = total_profit / amount

            if investor_yield >= target_return:
                st.success(f"✅ Подходящая стратегия: {name}")
                st.write(f"Gold доходность: {g_ret * 100:.2f}%/мес")
                st.write(f"Flip доходность: {f_ret * 100:.2f}%/6 мес")
                st.write(f"Algo доходность: {a_ret * 100:.2f}%/год")
                st.write(f"💡 Quadra: ${(g_inv + f_inv + a_inv) * QUADRA_PERF_FEE + mgmt_quadra:,.2f}")
                st.write(f"💡 Подрядчик: ${(a_amt * a_ret * months / 12) * THIRD_PERF_FEE + mgmt_third:,.2f}")
                found = True
                break
            a_ret += step
        if found:
            break
    if not found:
        st.error("❌ Не удалось достичь цели даже с максимальными параметрами.")

elif menu == "🔧 Кастомный калькулятор":
    gold_pct = st.number_input("Gold доля (%):", min_value=0.0, max_value=100.0) / 100
    flip_pct = st.number_input("Flip доля (%):", min_value=0.0, max_value=100.0) / 100
    algo_pct = st.number_input("Algo доля (%):", min_value=0.0, max_value=100.0) / 100

    total = gold_pct + flip_pct + algo_pct
    if abs(total - 1.0) > 0.01:
        st.warning(f"Сумма долей = {total*100:.2f}%. Она должна быть ровно 100%.")
    else:
        g_monthly = st.number_input("Доходность Gold (% в мес):") / 100
        f_6m = st.number_input("Доходность Flip (% за 6 мес):") / 100
        a_annual = st.number_input("Доходность Algo (% в год):") / 100

        q_mgmt = st.number_input("Quadra Management Fee (%):", value=2.0) / 100
        q_perf = st.number_input("Quadra Performance Fee (%):", value=20.0) / 100
        t_mgmt = st.number_input("Подрядчик Management Fee (%):", value=2.0) / 100
        t_perf = st.number_input("Подрядчик Performance Fee (%):", value=30.0) / 100

        g_amt = amount * gold_pct
        f_amt = amount * flip_pct
        a_amt = amount * algo_pct

        g_gross = g_amt * ((1 + g_monthly) ** min(9, months) - 1)
        g_fee = g_gross * q_perf
        g_net = g_gross - g_fee

        f_gross = f_amt * f_6m * (months // 6)
        f_fee = f_gross * q_perf
        f_net = f_gross - f_fee

        a_gross = a_amt * a_annual * months / 12
        a_third_fee = a_gross * t_perf
        a_net_after_third = a_gross - a_third_fee
        a_quadra_fee = a_net_after_third * q_perf
        a_net = a_net_after_third - a_quadra_fee

        mgmt_fee_q = amount * q_mgmt
        mgmt_fee_t = a_amt * t_mgmt

        investor_total = g_net + f_net + a_net - mgmt_fee_q - mgmt_fee_t
        quadra_total = g_fee + f_fee + a_quadra_fee + mgmt_fee_q
        third_total = a_third_fee + mgmt_fee_t

        st.success(f"📊 Доход инвестора: ${investor_total:,.2f} ({investor_total / amount * 100:.2f}%)")
        st.info(f"🏢 Доход Quadra: ${quadra_total:,.2f} ({quadra_total / amount * 100:.2f}%)")
        st.warning(f"💰 Доход подрядчика: ${third_total:,.2f} ({third_total / amount * 100:.2f}%)")
