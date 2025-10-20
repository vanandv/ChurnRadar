import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import lightgbm as lgb
import shap

st.set_page_config(page_title="ChurnRadar - Payment Retry Demo", layout="wide")

st.title("ChurnRadar — Payment-Failure Auto-Save Prototype")

st.markdown("Upload anonymized billing CSV or use sample data included in the repo.")

@st.cache_data
def load_sample():
    return pd.read_csv("sample_data.csv")

upload = st.file_uploader("Upload CSV", type=["csv"])
if upload is None:
    df = load_sample()
    st.info("Using sample_data.csv from repo")
else:
    df = pd.read_csv(upload)

st.write("Preview data", df.head(5))

# Ensure required columns exist
required = ["user_id","event_date","last_payment_status","failed_payment_count_90d","days_since_last_payment","tenure_months","ARPU","email_token","phone_token"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

# Basic feature engineering
df['failed_payment_count_90d'] = df['failed_payment_count_90d'].fillna(0).astype(int)
df['days_since_last_payment'] = df['days_since_last_payment'].fillna(999).astype(int)
df['tenure_months'] = df['tenure_months'].fillna(0).astype(float)
df['ARPU'] = df['ARPU'].fillna(df['ARPU'].median()).astype(float)
df['recent_failed'] = (df['failed_payment_count_90d'] > 0).astype(int)

st.subheader("Scoring method")
method = st.radio("Choose scoring method", ["Heuristic (fast)", "LightGBM (train if churn_30d available)"])

if method == "Heuristic (fast)":
    # Heuristic scoring
    mx = df['failed_payment_count_90d'].max() + 1
    df['score_30d'] = (
        0.5 * (df['failed_payment_count_90d'] / mx)
        + 0.4 * (df['recent_failed'])
        + 0.1 * (1 / (1 + df['days_since_last_payment']))
    ).clip(0,1)
else:
    if 'churn_30d' not in df.columns:
        st.warning("LightGBM requires historical target column 'churn_30d'. Falling back to heuristic.")
        mx = df['failed_payment_count_90d'].max() + 1
        df['score_30d'] = (
            0.5 * (df['failed_payment_count_90d'] / mx)
            + 0.4 * (df['recent_failed'])
            + 0.1 * (1 / (1 + df['days_since_last_payment']))
        ).clip(0,1)
    else:
        features = ['failed_payment_count_90d','days_since_last_payment','tenure_months','ARPU','recent_failed']
        train = df.dropna(subset=['churn_30d'])
        if len(train) < 50:
            st.warning("Not enough labeled rows for reliable LightGBM. Using heuristic.")
            mx = df['failed_payment_count_90d'].max() + 1
            df['score_30d'] = (
                0.5 * (df['failed_payment_count_90d'] / mx)
                + 0.4 * (df['recent_failed'])
                + 0.1 * (1 / (1 + df['days_since_last_payment']))
            ).clip(0,1)
        else:
            lgb_train = lgb.Dataset(train[features], label=train['churn_30d'])
            params = {'objective':'binary','metric':'auc','verbosity':-1,'seed':42}
            model = lgb.train(params, lgb_train, num_boost_round=100)
            df['score_30d'] = model.predict(df[features])

# Explain top drivers with a simple importance proxy (SHAP if model present)
st.subheader("Top-risk users")
top_n = st.number_input("Show top N users by score", value=10, min_value=1, max_value=100)
top = df.sort_values("score_30d", ascending=False).head(top_n).copy()

# Build top drivers text (simple)
def top_drivers_text(row):
    drivers = []
    if row['failed_payment_count_90d'] > 0:
        drivers.append(f"{int(row['failed_payment_count_90d'])} failed payments in 90d")
    if row['days_since_last_payment'] < 30:
        drivers.append(f"last payment {int(row['days_since_last_payment'])} days ago")
    if row['tenure_months'] < 3:
        drivers.append(f"low tenure {int(row['tenure_months'])} months")
    return drivers[:3]

top['top_drivers'] = top.apply(top_drivers_text, axis=1)

# Recommendation rule
def choose_action(row):
    if row['failed_payment_count_90d'] >= 2:
        return 'trigger_payment_retry'
    if row['score_30d'] > 0.7:
        return 'offer_discount'
    return 'notify_cs_team'

top['recommended_action'] = top.apply(choose_action, axis=1)
top['estimated_saved_revenue'] = (0.25 * top['ARPU'] * 3) - 5  # demo assumptions

st.dataframe(top[['user_id','score_30d','top_drivers','recommended_action','estimated_saved_revenue']])

st.subheader("Publish payload to webhook")
webhook_url = st.text_input("Webhook URL (enter webhook.site or sponsor endpoint)", value="https://webhook.site/")
selected = st.selectbox("Select user to publish", top['user_id'].tolist())
if st.button("Publish selected user"):
    row = top[top['user_id']==selected].iloc[0]
    payload = {
        "user_id": str(row['user_id']),
        "score_30d": float(row['score_30d']),
        "top_drivers": row['top_drivers'],
        "recommended_action": row['recommended_action'],
        "estimated_saved_revenue": float(row['estimated_saved_revenue']),
        "email_token": row['email_token'],
        "meta": {"model":"demo_v1"}
    }
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        st.success(f"Published. Webhook status: {resp.status_code}")
        st.json(payload)
    except Exception as e:
        st.error(f"Publish failed: {e}")
        st.json(payload)
