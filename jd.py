import streamlit as st
import requests


API_KEY  = st.secrets['API_KEY']
# Function to generate technical questions based on job description

def generate_technical_questions(job_description):
    jd = job_description.replace("\n","\n")

    technical_prompt = """Generate 5 technical interview questions based on given below Job Description. Include more questions to ask about technical definitions.
    Do not ask too many technical stuffs in single question. Keep the questions in short , simple terms and in well understanding manner. Each question must be in 15 words. Format the questions in python list in a numbered listicle way. \nBelow is the Job Description.""" + "\n" + str(jd)

    headers = {
        'Authorization': 'Bearer ' + API_KEY,
        'Content-Type': 'application/json',
    }

    json_data = {
        'model': 'gpt-4',
        'temperature': 0.5,
        'messages': [
            {
                'role': 'user',
                'content': technical_prompt
            }
        ],
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=json_data)

    res = response.json()

    if response.status_code == 200:
        print(res['choices'][0]['message']['content'])

    technical_question_list = list()
    for line in res['choices'][0]['message']['content'].split("\n"):
        technical_question_list.append(line)

    while ("" in technical_question_list):
        technical_question_list.remove("")
    print("@@@@@@@@@@@@")
    print(technical_question_list)

    technical_question_list = [i for i in technical_question_list if len(i) > 5]
    questions_without_index = [question.split(". ", 1)[1] for question in technical_question_list]
    questions_without_index = [question.split('?')[0] + '?' for question in questions_without_index]

    return questions_without_index

def main():
    st.header("Cognavi - JD Based Technical Interview Questions")

    # Text area to input job description
    job_description = st.text_area("Paste Job Description Here:")

    # Button to generate questions
    if st.button("Generate Questions"):
        if job_description:
            questions = generate_technical_questions(job_description)
            st.header("Technical Interview Questions:")
            for i, question in enumerate(questions, start=1):
                st.write(f"{i}. {question}")

if __name__ == "__main__":
    main()
