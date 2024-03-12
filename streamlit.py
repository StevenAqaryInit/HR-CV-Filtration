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

from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import AgGrid


nltk.download('stopwords')
nltk.download('punkt')


titles = []
count_matrix = []
cos_similarity = []
indexes = []

stop_words = set(stopwords.words('english'))
vectorizer = CountVectorizer(stop_words='english')

def show(df):
    # data = df.iloc[:, 1:]

    gd = GridOptionsBuilder.from_dataframe(df.iloc[:, 1:])
    gd.configure_selection(selection_mode='single'
                           , use_checkbox=True)
    grid_options = gd.build()

    grid_table = AgGrid(df
                        , gridOptions=grid_options
                        , fit_columns_on_grid_load=True
                        , reload_data=False
                        , allow_unsafe_jscode=True)
    
    # print(grid_table['selected_rows'])
    try:
        values = list(grid_table['selected_rows'][0].values())[1:]
        keys = list(grid_table['selected_rows'][0].keys())[1:]
    
        record = {}
        for key, value in zip(keys, values):
            record[key] = value
    except:
        pass

    return record




def filter_text(text_content):
    tokens = word_tokenize(text_content)
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    text = ' '.join(filtered_tokens)
    translation_table = str.maketrans('', '', string.punctuation)
    text = text.translate(translation_table)

    return text.lower()



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
    files_bytes = []

    for cv in files:
        print(cv.name)
        if cv.name.split('.')[1] == 'pdf':
            pdf_file = io.BytesIO(cv.read())
            cleaned_text = read_pdf(pdf_file)
            files_bytes.append(pdf_file)

        elif cv.name.split('.')[1] == 'docx' or cv.split('.')[1] == 'doc':
            docx_file = io.BytesIO(cv.read())
            cleaned_text = read_docx(docx_file)
            files_bytes.append(docx_file)

        df = pd.concat([df, pd.DataFrame([cleaned_text.lower()], columns=['cv'])], ignore_index=True)
        titles.append(cv.name)


    df['title'] = titles
    df['bytes'] = files_bytes

    return df



st.title('CV Filteration')

files = st.file_uploader('Upload files', accept_multiple_files=True, type=['PDF', 'DOCX', 'DOC'])
keywords = st.text_area('Enter the keywords here...')
contents = []
scores = []

df = pd.DataFrame()

# if st.button('Get Results'):
df = get_files_content(files)
clean_keywords = filter_text(keywords)

for cv in df.iloc[:, 0].values.tolist():
    matrix = vectorizer.fit_transform([cv, clean_keywords])
    scores.append(cosine_similarity(matrix)[0][1]) 
    
df['scores'] = scores
df['scores'] = df['scores'] * 100
# st.dataframe(df[['title', 'scores']].sort_values(by='scores', ascending=False), width=1000, height=500)

# print(df)
# st.dataframe(df[['title', 'scores']].sort_values(by='scores', ascending=False).drop_duplicates())

record = show(df[['bytes', 'title', 'scores']].sort_values(by='scores', ascending=False).drop_duplicates())
row = df[df['title']==record['title']]
print(row)



if st.button('Download'):
    try:
        # print(row['bytes'].values[0])
        # with open(row['title'].values[0], 'wb') as pdf_file:
        #     pdf_file.write(row['bytes'].values[0])

        for file in files:
            if file.name == record['title']:
                with open(row['title'].values[0], 'wb') as save_file:
                    save_file.write(file.getbuffer())

        st.success('Saved...')
    except:
        pass



