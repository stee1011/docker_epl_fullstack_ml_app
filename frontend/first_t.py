# filename:first_t.py

import streamlit as st
import requests
import json

st.set_page_config(page_title="EPL Player Minutes Predictor", page_icon="", layout="centered")

st.title("EPL Minutes Predictor")
st.markdown("Paste full **JSON player data** and get the predicted total minutes played ")

# Input fields
api_url = st.text_input("API Endpoint URL", "http://localhost:8002/predict")
auth_token = st.text_input("Bearer Token", type="password")

# JSON input
st.markdown("### Paste Player Data (as JSON):")
default_json = {
    "player_name": "Harry Kane",
    "club": "Tottenham Hotspur",
    "nationality": "England",
    "position": "FWD",
    "appearances": 30,
    "minutes": 2700,
    "shots": 120,
    "shots_on_target": 80,
    "touches": 2000,
    "passes": 1400,
    "successful_passes": 1200,
    "crosses": 50,
    "successful_crosses": 20,
    "carries": 400,
    "progressive_carries": 180,
    "tackles": 15,
    "interceptions": 10,
    "clearances": 5,
    "conversion_rate": 28.5,
    "pass_accuracy": 85.7,
    "cross_accuracy": 40.0
}
json_input = st.text_area("JSON Data", value=json.dumps(default_json, indent=2), height=400)

# Submit button
if st.button("Predict Minutes"):
    if not api_url or not auth_token:
        st.error("Please provide both the API URL and Bearer token.")
    else:
        try:
            player_data = json.loads(json_input)
        except json.JSONDecodeError:
            st.error("Invalid JSON. Please check your formatting.")
            st.stop()

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        with st.spinner(" Sending data to the prediction API..."):
            try:
                response = requests.post(api_url, json=player_data, headers=headers)
                response.raise_for_status()
                result = response.json()
                predicted_minutes = result.get("predicted_minutes", None)

                if predicted_minutes is not None:
                    st.success(f"Predicted Total Minutes Played: **{predicted_minutes} minutes** ")
                else:
                    st.warning(" Response received, but no 'predicted_minutes' found in it.")

            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
