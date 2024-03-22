from PIL import Image, ImageFont, ImageDraw
import pandas as pd
import os
import streamlit as st

FONT_PATH = 'Pacifico-Regular.ttf'


def generate_certificates(template: st.image,
                          x_coordinate: int,
                          y_coordinate: int,
                          names: pd.DataFrame,
                          random_name: str,
                          progress_bar: st.progress,
                          total_names: int,
                          font_size: int):
    folder_output: str = 'certificates'
    os.makedirs(folder_output, exist_ok=True)
    os.makedirs(rf'.\certificates\{random_name}', exist_ok=True)
    user_output_folder = rf'.\certificates\{random_name}'
    counter = 0
    for index, row in names.iterrows():
        full_name = row[0]
        certificate_img = Image.open(template).copy()
        font = ImageFont.truetype(FONT_PATH, font_size)
        draw = ImageDraw.Draw(certificate_img)
        text_x = x_coordinate
        text_y = y_coordinate
        draw.text((text_x, text_y), full_name, (35, 57, 75), font=font)
        certificate_filename = os.path.join(user_output_folder, f"{full_name.replace(' ', '_')}.png")
        certificate_img.save(certificate_filename)
        counter += 1
        progress_percent = int((counter/total_names)*100)
        progress_bar.progress(progress_percent)
