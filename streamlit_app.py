import streamlit as st
import requests
import json
import ollama
import time
import os
import replicate

# def stream_data(text, delay:float=0.02):
#     for word in text.split('\n'):
#         yield word + " "
#         time.sleep(delay)

# # Streamlit app title
# st.title("Enhanced Query Tool with LLaMA")
import re

def clean_response(response):
    # Define unwanted phrases
    unwanted_phrases = [
        "Sure, I'd be happy to help!",
        "I'm happy to assist you with that.",
        "Sure thing!",
        "Certainly!"
    ]
    
    # Create a regex pattern to match any of the unwanted phrases
    pattern = re.compile(r'\b(?:' + '|'.join(re.escape(phrase) for phrase in unwanted_phrases) + r')\b', re.IGNORECASE)
    
    # Remove the unwanted phrases
    clean_text = pattern.sub("", response).strip()
    
    # Optionally, you can add a step to ensure the first character is capitalized if it became lowercase after removal
    if clean_text and not clean_text[0].isupper():
        clean_text = clean_text[0].upper() + clean_text[1:]
    
    return clean_text


st.title('🦙💬 Llama 2 Agricultural Chatbot')

with st.sidebar:
    st.title('🦙💬 Llama 2 Chatbot')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
        os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)
    # st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

# Function for generating LLaMA response tailored to agricultural questions
def generate_llama_response(user_question, similar_question, best_answer_similar_question, temperature=0.7, top_p=1.0, max_length=150):
    # Construct the detailed prompt with context about the task and specifics of the query
    prompt = f"Context: Our system answers agricultural questions by performing a semantic search to find the most relevant previously answered questions and answers in our database.\nUser Question: {user_question}\nSimilar Question: {similar_question}\nBest Answer to the Similar Question: {best_answer_similar_question}\nBased on the above, what would be the best response to the user's question? Please provide a concise answer in less than 60 words. "
    # Construct the detailed prompt with context about the task and specifics of the query
    prompt = f"Context: Our system answers agricultural questions by performing a semantic search to find the most relevant previously answered questions and answers in our database.\nUser Question: {user_question}\nSimilar Question: {similar_question}\nBest Answer to the Similar Question: {best_answer_similar_question}\nDirectly based on the above, provide the best concise answer for the user's question without restating the question. Please provide a concise answer in less than 60 words. Provide a direct and practical recommendation suitable for the user's query without any additional explanations or introductions.Start stating the answer directly. e.g The gestation period for a cow is....... Do not tell me how happy you would love to help!"
    prompt = f"""Context: This is an agricultural advice tool. The system uses previous Q&A data to generate direct and concise responses to user queries.
        User Question: {user_question}
        Similar Question: {similar_question}
        Best Answer to the Similar Question: {best_answer_similar_question}
        Instruction: Provide a direct and practical answer to the user's question based on the best answer to a similar question. Start your response with the factual answer, avoiding any greetings or introductory phrases. Use this and speak/Act like an Expert and Answer in less than 60 words. Remember no introductory phases and No Preamble!"""
    # prompt = f"""
    #     [Context: This tool assists users by providing answers to agricultural questions based on a database of similar past questions and answers. The response should directly address the user's question using information from the most relevant similar question and answer without unnecessary introductions or fluff.]

    #     [User Question: {user_question}]
    #     [Similar Question: {similar_question}]
    #     [Best Answer to Similar Question: {best_answer_similar_question}]

    #     [Response Instruction: Directly answer the user's question using the details from the best answer provided to the similar question. Start immediately with the factual response, avoid greetings, and ensure the answer is concise and to the point.]
    #     """

    # Call to LLaMA model
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5',
                           input={"prompt": prompt,
                                  "temperature": temperature,
                                  "top_p": top_p,
                                  "max_length": max_length,
                                  "repetition_penalty": 1})
    # Assuming the model returns a dictionary containing the response text
    return output

# Form to input the question and other parameters
with st.form("query_form"):
    question = st.text_input("Question", value="What is the best fertilizer for wheat?")
    submitted = st.form_submit_button("Submit")

if submitted:
    # API URL for your backend service
    api_url = "http://35.232.247.73:8000/query/"

    # Request headers and data
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {
        "user_id": "415",
        "question": question,
        "language": "English",
        "category": "",
        "sub_category": None,
        "topic": "",
        "sub_topic": None,
        "location": None,
        "simple_response": False
    }

    # Fetching data from your API
    api_response = requests.post(api_url, headers=headers, data=json.dumps(data))

    if api_response.status_code == 200:
        api_response_json = api_response.json()
        similar_question = api_response_json.get('similar_questions')[0]  # Example access
        similar_answer = api_response_json.get('answers')[0]  # Example access
        print(api_response_json)

        # Print the questions and answers for comparison
        st.write("### User's Question:")
        st.text(question)
        st.write("### Similar Question Found:")
        st.text(similar_question)
        # st.write("### Best Answer to Similar Question:")
        # st.text(similar_answer)      
            # Using text area for long answers
        st.text_area("Best Answer to Similar Question:", value=similar_answer, height=150) 
        st.write("### Modified LLM Response:")

    
    with st.spinner("Thinking..."):
        response = generate_llama_response(
            user_question=question,
            similar_question=similar_question,
            best_answer_similar_question=similar_answer,
        )

        # Clean the response to remove any unwanted introductory phrases
        # response = clean_response(response)
        placeholder = st.empty()
        full_response = ''
        for item in response:
            full_response += item
            placeholder.markdown(full_response)
        placeholder.markdown(full_response)

#         # Creating the prompt for the LLaMA model
#         prompt = f"Context: Our system answers agricultural questions by performing a semantic search to find the most relevant previously answered questions and answers in our database.\nUser Question: {question}\nSimilar Question: {similar_question}\nBest Answer to the Similar Question: {similar_answer}\nBased on the above, what would be the best response to the user's question? Please provide a concise answer in less than 60 words."


#         with st.spinner(" Thinking ......."):
#             # Using LLaMA for enhanced response
#             llama_response = ollama.chat(
#                 model='phi3',
#                 messages=[{'role': 'user', 'content': prompt}],
#                 # stream=True
#             )

#             # enhanced_answer = next(llama_response)['message']['content']
#             enhanced_answer = llama_response['message']['content']
#             print(enhanced_answer)
        
#             # Display the enhanced response
#             # st.success("Enhanced query successful!")
#             st.write_stream(stream_data(enhanced_answer))
#     else:
#         st.error(f"Failed to query. Status code: {api_response.status_code}")


