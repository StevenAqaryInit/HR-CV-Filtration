
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
import concurrent.futures
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
    try:
        gd = GridOptionsBuilder.from_dataframe(df.iloc[:, 1:])
        gd.configure_selection(selection_mode='single'
                            , use_checkbox=True)
        grid_options = gd.build()

        grid_table = AgGrid(df
                            , gridOptions=grid_options
                            , fit_columns_on_grid_load=True
                            , reload_data=False
                            , allow_unsafe_jscode=True
                            , height=500)
        
        values = list(grid_table['selected_rows'][0].values())[1:]
        keys = list(grid_table['selected_rows'][0].keys())[1:]
    
        record = {}
        for key, value in zip(keys, values):
            record[key] = value

        return record
    except:
        pass

    

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




def get_files_content(cv):
    print(cv)
    if cv.name.split('.')[-1] == 'pdf':
        bytes_file = io.BytesIO(cv.read())
        cleaned_text = read_pdf(bytes_file)

    elif cv.name.split('.')[-1] == 'docx' or cv.split('.')[-1] == 'doc':
        bytes_file = io.BytesIO(cv.read())
        cleaned_text = read_docx(bytes_file)

    return cleaned_text, bytes_file

    


def run_on_threads(files):
    df = pd.DataFrame()
    files_bytes = []

    for cv in files:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            print(cv.name)
            titles.append(cv.name)
            thread = executor.submit(get_files_content, cv)
            result_value = thread.result()
            files_bytes.append(result_value[1])
            df = pd.concat([df, pd.DataFrame([result_value[0].lower()], columns=['cv'])], ignore_index=True)
            
    df['title'] = titles
    df['bytes'] = files_bytes

    return df



st.title('CV Filteration')

files = st.file_uploader('Upload files', accept_multiple_files=True, type=['PDF', 'DOCX', 'DOC'])
keywords = st.text_area('Enter the keywords here...')
contents = []
scores = []

# df = pd.DataFrame()

# if st.button('Get Results'):
df = run_on_threads(files)
clean_keywords = filter_text(keywords)



def get_scores(cv, clean_keywords):
    matrix = vectorizer.fit_transform([cv, clean_keywords])
    scores = cosine_similarity(matrix)[0][1]

    return scores


if clean_keywords != '':
    for cv in df.iloc[:, 0].values.tolist():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            thread = executor.submit(get_scores, cv, clean_keywords)
            result_value = thread.result()
            scores.append(result_value)
        

    df['scores'] = scores
    df['scores'] = df['scores'] * 100

    record = show(df[['bytes', 'title', 'scores']].sort_values(by='scores', ascending=False).drop_duplicates())
    try:
        row = df[df['title']==record['title']]
        print(row)
    except:
            pass


    try:
        for file in files:
            if file.name == record['title']:
                st.download_button(
                    label="Download file",
                    data=bytes(file.getbuffer()),
                    file_name=row['title'].values[0],
                )
    except:
        pass

else:
    st.error('Enter some keywords...')


