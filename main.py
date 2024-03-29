import streamlit as st
from PIL import Image
from PIL.ImageDraw import Draw
from PIL import ImageFont
import matplotlib.pyplot as plt
import pandas as pd
from certificate_generator import generate_certificates
import zipfile
import os
from random_folder import generate_random_string
import shutil
from datetime import datetime, timedelta
import time
from clear_files import file_deleter

# TODO: add fonts

OUTPUT_FOLDER = 'zips'
FONT_PATH = 'Pacifico-Regular.ttf'


FAVICO = 'favico.png'
favico = Image.open(FAVICO)
st.set_page_config(
    page_title='Certifier',
    page_icon=favico
)


if 'x_coordinate' and 'y_coordinate' and 'image' and 'certifiable_names' not in st.session_state:
    st.session_state.x_coordinate = None
    st.session_state.y_coordinate = None
    st.session_state.font_size = None
    st.session_state.image = None
    st.session_state.certifiable_names = pd.DataFrame({})
    st.session_state.user_folder = None


def delete_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)


def main_page():
    st.title('Hi, welcome to certifier.')
    st.header('Heres how you can bulk generate certificates for free!')
    st.subheader('1. Choose a certificate template which you want to add names to.')
    st.caption('Choose the x and y coordinates and size for the text ')
    st.subheader('2. Upload the list of names in csv format')
    st.caption('and choose the batch you want to generate certificates for.At a time currently you can only generate 20 certificates at max.')
    st.subheader('3. Generate certificates')
    st.caption('You dont really have to do much. just click a button.')
    st.subheader('4. Generate zip and download all the certificates 🥳')
    st.header('About this project')
    st.write('This website allows you to bulk generate certificates. This saves manual effort for making certificates for attendees in a session, event, etc.')
    file_deleter()


def upload_template_page():
    if st.session_state['image'] is None:
        st.title('Upload a template ')
        uploaded_file = st.file_uploader('Choose a template', type=['jpg', 'png'], accept_multiple_files=False)
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split('.')[-1]
            if file_extension.lower() not in ['jpg', 'png', 'jpeg']:
                st.error('Please upload a jpg or png file.')
                return
            image = Image.open(uploaded_file)
            width, height = image.size
            x_coordinate = st.slider('Select X-coordinate', 0, width - 1, width // 2)
            y_coordinate = st.slider('Select Y-coordinate', 0, height - 1, height // 2)
            # x_coordinate = st.slider('Select X-coordinate', 0, width - 1, 633)
            # y_coordinate = st.slider('Select Y-coordinate', 0, height - 1, 654)
            height_of_font = st.slider('Select Font size', 0, 200, 100)
            fig, ax = plt.subplots()
            ax.imshow(image)
            draw = Draw(image)
            font = ImageFont.truetype(FONT_PATH, height_of_font)
            draw.text((x_coordinate, y_coordinate), 'Lorem Ipusium', (35, 57, 75), font=font)
            # draw.rectangle([x_coordinate - 5, y_coordinate - 5, x_coordinate + 5, y_coordinate + 5],
            #                outline='red', width=2)
            st.image(image, caption='Select starting position for names', use_column_width=True)
            next_button = st.button('Confirm Template ✅')
            if next_button:
                st.write('template confirmed please move to next step ✅✅')
                st.session_state.x_coordinate = x_coordinate
                st.session_state.y_coordinate = y_coordinate
                st.session_state.font_size = height_of_font
                st.session_state.image = uploaded_file
    else:
        st.title('Selected template ')
        st.image(st.session_state['image'])


def upload_csv_page():
    df = st.session_state['certifiable_names']
    if df.empty:
        st.title('Upload a file with list of names ')
        st.write('Please upload a CSV file containing names to be certified.')
        uploaded_csv_file = st.file_uploader('Choose a file', type=['csv'])
        if uploaded_csv_file is not None:
            file_extension = uploaded_csv_file.name.split('.')[-1]
            if file_extension.lower() not in ['csv']:
                st.error('Please upload a CSV file.')
                return

            if file_extension.lower() == 'csv':
                names_df = pd.read_csv(uploaded_csv_file, header=None)
                selected_set = st.selectbox('Select a set of names for certification', range(0, len(names_df), 20),
                                            index=0)
                st.write(f'Selected set of names (Set {selected_set // 20 + 1}):')
                selected_names_df = names_df.iloc[selected_set:selected_set + 20]
                st.dataframe(selected_names_df, hide_index=True, column_config=None)
                next_button = st.button('Confirm names to be certified ✅')
                if next_button:
                    st.write('names confirmed please move to next step ✅✅')
                    st.session_state.certifiable_names = selected_names_df
    else:
        st.title('Following names will be certified')
        st.write(st.session_state['certifiable_names'])


def generate_certificate_page():
    df = st.session_state['certifiable_names']
    if df.empty:
        st.error('Please select names to be certified.')
    if st.session_state['image'] is None:
        st.error('Please provide with a template.')
    if (not df.empty) and st.session_state['image'] is not None:
        st.title('Click button to generate certificates')
        generate_button = st.button('Generate certificates')
        if generate_button:
            # TODO: check if already exist
            user_folder = generate_random_string()
            st.session_state.user_folder = user_folder
            template = st.session_state['image']
            x_coordinate = st.session_state['x_coordinate']
            y_coordinate = st.session_state['y_coordinate']
            names = st.session_state['certifiable_names']
            font_size = st.session_state['font_size']
            total_names = names.shape[0]
            progress_bar = st.progress(0)
            generate_certificates(template, x_coordinate, y_coordinate, names, user_folder, progress_bar, total_names, font_size)
            progress_bar.empty()
            st.balloons()
            st.success('Certificates generated! 🥳')
            st.write('proceed to download page to download certificates')


def create_zip(images_folder, zip_file_name, output_folder):
    # Get the list of images in the folder
    image_files = [os.path.join(images_folder, f) for f in os.listdir(images_folder) if
                   os.path.isfile(os.path.join(images_folder, f))]
    # Create a Zip file
    with zipfile.ZipFile(os.path.join(output_folder, zip_file_name), 'w') as zipf:
        for image_file in image_files:
            zipf.write(image_file, os.path.basename(image_file))


def download_the_zip_page():
    st.title('🌟 Download all the certificates 🌟')
    user_folder = st.session_state['user_folder']
    certificates_folder = rf'.\certificates\{user_folder}'
    create_zip_button = st.button('Create Zip')
    if create_zip_button:
        if not os.path.exists(rf'.\certificates\{user_folder}'):
            st.warning('No images generated yet!')
        else:
            if not os.path.exists(OUTPUT_FOLDER):
                os.makedirs(OUTPUT_FOLDER)
            create_zip(certificates_folder, f'{user_folder}.zip', OUTPUT_FOLDER)
            st.success('Images zipped successfully! Click below to download.')
            shutil.rmtree(certificates_folder)
            with open(os.path.join(OUTPUT_FOLDER, f'{user_folder}.zip'), 'rb') as f:
                bytes_data = f.read()
            st.download_button(label='Download', data=bytes_data,
                                                 file_name=rf'.\zips\{user_folder}.zip', mime='application/zip')
            delete_file(rf'.\zips\{user_folder}.zip')


page_names_to_funcs = {
    'Main Page': main_page,
    'Upload a template': upload_template_page,
    'Upload file with list of names': upload_csv_page,
    'Generate Certificates': generate_certificate_page,
    'Download the certificates': download_the_zip_page,
}

selected_page = st.sidebar.selectbox('Select a page', page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
