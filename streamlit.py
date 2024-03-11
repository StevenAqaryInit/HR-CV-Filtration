import streamlit as st
import os
import pandas as pd
import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import io


nltk.download('stopwords')
nltk.download('punkt')

titles = []
count_matrix = []
cos_similarity = []
indexes = []

stop_words = set(stopwords.words('english'))
vectorizer = CountVectorizer(stop_words='english')

def get_files_content(files):
    df = pd.DataFrame()
    for cv in files:
        pdf_file = io.BytesIO(cv.read())
        pdfReader = PyPDF2.PdfReader(pdf_file)

        pages_list = ''
        for page in pdfReader.pages:
            pages_list += ' '.join(page.extract_text().split('\n'))
            modified_text = ' '.join(pages_list.split())

            tokens = word_tokenize(modified_text)
            filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
            text = ' '.join(filtered_tokens)
            translation_table = str.maketrans('', '', string.punctuation)
            cleaned_text = text.translate(translation_table)

        df = pd.concat([df, pd.DataFrame([cleaned_text.lower()], columns=['cv'])], ignore_index=True)
        titles.append(cv.name)

    df['title'] = titles

    return df



st.title('CV Filteration')

files = st.file_uploader('Upload files', accept_multiple_files=True, type=['PDF'])
keywords = st.text_input('Enter the keywords here...')
contents = []
scores = []


if st.button('Get Results'):
    df = get_files_content(files)
    
    for cv in df.iloc[:, 0].values.tolist():
        matrix = vectorizer.fit_transform([cv, keywords])
        scores.append(cosine_similarity(matrix)[0][1]) 
        
    df['scores'] = scores
    df['scores'] = df['scores']*100
    st.dataframe(df[['title', 'scores']].sort_values(by='scores', ascending=False), width=1000, height=500)








