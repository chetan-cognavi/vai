import streamlit as st
import requests, random


API_KEY  = st.secrets['API_KEY']
# Function to generate technical questions based on job description

# Function to generate resume-based questions
def generate_resume_questions(resume_summary):
    jd = resume_summary.replace("\n", "\n")

    resume_summary_prompt = """Generate 5 technical interview questions based on given below Resume Summary. 
    Include more questions to ask about technical definitions. Include the questions which starts with what to evaluate the technical knowledge by definitions.
    Start the first question with candidate name. Do not ask more than 2 technical skills  in single question. Keep the questions in short , simple terms and in well understanding manner. Each question must be in 15 words. Format the questions in python list in a numbered listicle way. \nBelow is the Job Description.""" + "\n" + str(
        jd)

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
                'content': resume_summary_prompt
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

def generate_technical_questions(job_description):
    jd = job_description.replace("\n","\n")

    technical_prompt = """Generate 5 technical interview questions based on given below Job Description. Include  questions to ask about technical definitions.Include the questions which starts with what to evaluate the technical knowledge by definitions.
    Do not ask more than 2 technical skills  in single question. Keep the questions in short , simple terms and in well understanding manner. Each question must be in 15 words. Format the questions in python list in a numbered listicle way. \nBelow is the Job Description.""" + "\n" + str(jd)

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
    if 'jd_questions' not in st.session_state:
        st.session_state.jd_questions = []
    if 'resume_questions' not in st.session_state:
        st.session_state.resume_questions = []

    st.set_page_config(layout="wide")

    st.header("Cognavi - JD & Resume Based Technical Interview Questions")

    col1, col2 = st.columns(2)

    with col1:
        job_description = st.text_area("Paste Job Description Here:")
        if st.button("Generate JD Questions"):
            if job_description:
                st.session_state.jd_questions = generate_technical_questions(job_description)

    with col2:
        resume_summary = st.text_area("Paste Resume Summary Here:")
        if st.button("Generate Resume Questions"):
            if resume_summary:
                st.session_state.resume_questions = generate_resume_questions(resume_summary)

    st.markdown("---")

    # st.header("Generated Questions:")
    if st.session_state.jd_questions:
        st.header("Job Description Based Technical Interview Questions:")
        for i, question in enumerate(st.session_state.jd_questions, start=1):
            st.write(f"{i}. {question}")

    if st.session_state.resume_questions:
        st.header("Resume Based Technical Interview Questions:")
        for i, question in enumerate(st.session_state.resume_questions, start=1):
            st.write(f"{i}. {question}")

    st.markdown("---")

    if st.button("Randomly Pick 5 Questions"):
        combined_questions = st.session_state.jd_questions + st.session_state.resume_questions
        num_questions = min(5, len(combined_questions))
        random_questions = random.sample(combined_questions, num_questions)
        st.header("Randomly Picked Questions:")
        for i, question in enumerate(random_questions, start=1):
            st.write(f"{i}. {question}")

    if st.button("Reset"):
        st.session_state.jd_questions = []
        st.session_state.resume_questions = []
        st.session_state.job_description = ""
        st.session_state.resume_summary = ""

if __name__ == "__main__":
    main()
