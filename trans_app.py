import streamlit as st
import boto3
import time
import urllib.request
import json
import uuid


DEFAULT_BUCKET_NAME = "transcribe-ytube"

def generate_unique_job_name():
    return 'transcription_job_' + str(uuid.uuid4())


def upload_to_s3(file_path, bucket_name, object_name):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_path, bucket_name, object_name)
        return True
    except Exception as e:
        st.error(f"Error uploading file to S3: {e}")
        return False


def transcribe_video(file_uri, job_name):
    transcribe = boto3.client('transcribe')

    try:
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': file_uri},
            MediaFormat='webm',
            LanguageCode='en-US'  # Change this to match the language of the audio if needed
        )
        return response['TranscriptionJob']['TranscriptionJobName']
    except Exception as e:
        st.error(f"Error starting transcription job: {e}")
        return None


def get_transcription_result(job_name):
    transcribe = boto3.client('transcribe')

    while True:
        response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if response['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)

    if response['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
        response = urllib.request.urlopen(transcript_uri)
        transcript = response.read().decode('utf-8')
        return transcript
    else:
        return None


def display_transcript_with_timestamps(transcript):
    parsed_transcript = json.loads(transcript)
    items = parsed_transcript['results']['items']
    current_sentence = ""
    current_timestamp = None
    for item in items:
        if item['type'] == 'pronunciation':
            word = item['alternatives'][0]['content']
            current_sentence += word + " "
            if word.endswith('.'):
                if current_sentence.strip():
                    st.write(f"**{current_sentence.strip()}** --> {current_timestamp} seconds")
                    current_sentence = ""
            if current_timestamp is None:
                current_timestamp = item['start_time']
    if current_sentence.strip():
        st.write(f"**{current_sentence.strip()}** --> {current_timestamp} seconds")


def main():
    st.title("Cognavi - Video Transcription App")

    st.write("""
    ## Upload Local Video File or Provide S3 URI
    """)

    method = st.radio("Select Method", ("Upload Local File", "Provide S3 URI"))

    if method == "Upload Local File":
        uploaded_file = st.file_uploader("Upload Video File", type=["mp4", "webm"])
        bucket_name = DEFAULT_BUCKET_NAME
        if uploaded_file:
            file_name = uploaded_file.name
            with open(file_name, "wb") as f:
                f.write(uploaded_file.getbuffer())
    else:
        uploaded_file = None
        file_name = None
        bucket_name = None
        s3_uri = st.text_input("Enter S3 URI")

    if st.button("Transcribe"):
        st.info("Transcription process initiated. Please wait...")

        if uploaded_file:
            if file_name and bucket_name:
                object_name = f"uploaded_{file_name}"
                if upload_to_s3(file_name, bucket_name, object_name):
                    file_uri = f"s3://{bucket_name}/{object_name}"
                    job_name = generate_unique_job_name()
                    job_name = transcribe_video(file_uri, job_name)
                    if job_name:
                        transcript = get_transcription_result(job_name)
                        if transcript:
                            st.success("Transcription completed successfully.")
                            st.write("Transcript:")
                            display_transcript_with_timestamps(transcript)
                        else:
                            st.error("Failed to get transcription result.")
                    else:
                        st.error("Transcription job failed to start.")
                else:
                    st.error("Failed to upload file to S3.")
            else:
                st.error("Please select a file.")
        elif s3_uri:
            job_name = generate_unique_job_name()
            job_name = transcribe_video(s3_uri, job_name)
            if job_name:
                transcript = get_transcription_result(job_name)
                if transcript:
                    st.success("Transcription completed successfully.")
                    st.write("Transcript:")
                    display_transcript_with_timestamps(transcript)
                else:
                    st.error("Failed to get transcription result.")
            else:
                st.error("Transcription job failed to start.")
        else:
            st.error("Please upload a video file or provide an S3 URI.")


if __name__ == "__main__":
    main()
