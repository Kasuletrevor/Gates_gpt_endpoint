import streamlit as st
import requests
import json
import ollama

# Streamlit app title
st.title("GatesGPT API Query Tool")


# language_options = ["English", "Luganda"]
language = "English"
    # category_options = ["Animal", "Crop"]
    # category = st.selectbox("Category", options=category_options)
category = ""
topic = ""
sub_topic = ""
sub_category = ""
location= ""
    # topic = st.text_input("Topic", value="Fertilization")
    # sub_topic = st.text_input("Sub Topic", value="")
    # location = st.text_input("Location", value="")

# Form to input the question and other parameters
with st.form("query_form"):
    # user_id = 315
    question = st.text_input("Question", value="What is the best fertilizer for wheat?")
    # language_options = ["English", "Luganda"]
    # language = st.selectbox("Language", options=language_options, index=0)
    # category_options = ["Animal", "Crop"]
    # category = st.selectbox("Category", options=category_options)
    # sub_category = st.text_input("Sub Category", value="")
    # topic = st.text_input("Topic", value="Fertilization")
    # sub_topic = st.text_input("Sub Topic", value="")
    # location = st.text_input("Location", value="")
    submitted = st.form_submit_button("Submit")

if submitted:
    # API URL
    url = "http://35.239.70.68:8000/query/"
    url = "http://35.232.247.73:8000/query/"
    
    # Request headers
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Request data
    data = {
        "user_id": "415",
        "question": question,
        "language": language,
        "category": category,
        "sub_category": sub_category or None,
        "topic": topic,
        "sub_topic": sub_topic or None,
        "location": location or None,
        "simple_response": False
    }
    
    # Send the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        # Display the response
        st.success("Query successful!")
        st.json(response.json())
    else:
        st.error(f"Failed to query. Status code: {response.status_code}")
