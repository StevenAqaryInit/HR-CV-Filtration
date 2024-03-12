import streamlit as st
import pandas as pd
import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import io
from docx import Document
import nltk


nltk.download('stopwords')
nltk.download('punkt')



titles = []
count_matrix = []
cos_similarity = []
indexes = []

stop_words = set(stopwords.words('english'))
vectorizer = CountVectorizer(stop_words='english')



def filter_text(text_content):
    tokens = word_tokenize(text_content)
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    text = ' '.join(filtered_tokens)
    translation_table = str.maketrans('', '', string.punctuation)
    text = text.translate(translation_table)

    return text


def read_docx(file):
    doc = Document(file)
    text_content = ""
    for paragraph in doc.paragraphs:
        text_content += ' '.join(paragraph.text.split('\n'))

    cleaned_text = filter_text(text_content)
    return cleaned_text



def read_pdf(file):
    pdfReader = PyPDF2.PdfReader(file)

    pages_list = ''
    for page in pdfReader.pages:
        pages_list += ' '.join(page.extract_text().split('\n'))

    cleaned_text = filter_text(pages_list)
    return cleaned_text




def get_files_content(files):
    df = pd.DataFrame()
    for cv in files:
        if cv.name.split('.')[1] == 'pdf':
            pdf_file = io.BytesIO(cv.read())
            cleaned_text = read_pdf(pdf_file)

        elif cv.name.split('.')[1] == 'docx' or cv.split('.')[1] == 'doc':
            docx_file = io.BytesIO(cv.read())
            cleaned_text = read_docx(docx_file)

        df = pd.concat([df, pd.DataFrame([cleaned_text.lower()], columns=['cv'])], ignore_index=True)
        titles.append(cv.name)


    df['title'] = titles
    return df.drop_duplicates()




st.title('CV Filteration')

files = st.file_uploader('Upload files', accept_multiple_files=True, type=['PDF', 'DOCX', 'DOC'])
keywords = st.text_input('Enter the keywords here...')
contents = []
scores = []


if st.button('Get Results'):
    df = get_files_content(files)
    clean_keywords = filter_text(keywords)

    for cv in df.iloc[:, 0].values.tolist():
        print(clean_keywords)
        matrix = vectorizer.fit_transform([cv, clean_keywords])
        scores.append(cosine_similarity(matrix)[0][1]) 
        

    df['scores'] = scores
    df['scores'] = df['scores'] * 100
    st.dataframe(df[['title', 'scores']].sort_values(by='scores', ascending=False), width=1000, height=500)

