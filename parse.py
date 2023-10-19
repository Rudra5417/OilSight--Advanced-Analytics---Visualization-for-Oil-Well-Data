import os
from pypdf import PdfReader

import pandas as pd
from collections import Counter
from nltk import word_tokenize, WordNetLemmatizer
import nltk
import fitz
from fitz import Point, Rect
import editdistance
from tqdm import tqdm
import re
import mysql.connector
from mysql.connector import Error
import getpass


nltk.download('wordnet')
folder_path = 'DSCI560_lab5'
output_pdf_path = "DSCI560_lab5_p"
password = getpass.getpass("Enter your password: ")

pdfs = []
d = 0
# DEBUG = "W28654.pdf"
DEBUG = None
pdf_files = [filename for filename in os.listdir(folder_path) if filename.endswith('.pdf') and (not DEBUG or filename == DEBUG)]

output_csv = {}

for filename in tqdm(pdf_files, desc="Scanning Files"):
    if filename.endswith('.pdf') and (not DEBUG or filename == DEBUG):
        output_csv[filename] = {}

        if DEBUG: print(f"Scanning File: {filename}")
        pdf_path = os.path.join(folder_path, filename)
        pdf = []
        pdf_reader = PdfReader(pdf_path)
        c  = 0
        pdf.append([])
        mupdf = fitz.open(pdf_path) 

        for page in pdf_reader.pages:
            page_bboxes = {}
            try:
                words = word_tokenize(page.extract_text())
                words = [w.lower() for w in words]
                word_freq = Counter(words)
                
                # Calculate the incidence of "stimulations" and related lemmas
                incidence = (word_freq["stimulation"] + word_freq["stimulated"])/(sum(word_freq.values()) + 1)

                # Check if this PDF has a higher incidence
                if incidence > 0.005 and word_freq["stimulation"] >= 4:
                    stim_page = mupdf[c]
                    words = stim_page.get_text("words")
                    
                    prev_date = None
                    date_found = False
                    formation_found = False
                    top_found = False
                    bot_found = False
                    stages_found = False
                    volume_found = False
                    units_found = False
                    type_found = False
                    acid_found = False
                    proppant_found = False
                    pressure_found = False
                    rate_found = False
                    details_found = False

                    all_found = all([
                        date_found,
                        formation_found,
                        top_found,
                        bot_found,
                        stages_found,
                        volume_found,
                        units_found,
                        type_found,
                        acid_found,
                        proppant_found,
                        pressure_found,
                        rate_found,
                        details_found
                    ])

                    for word in words:
                        if editdistance.eval(word[4], "Date") <=2 and not date_found:
                            prev_date = word
                        elif editdistance.eval(word[4], "Stimulated") <=4 and not date_found:
                            page_bboxes["Date Stimulated"] = ','.join(stim_page.get_textbox(Rect(Point(prev_date[0], prev_date[1]), Point(prev_date[0] + 50, prev_date[1] + 10))).split())
                            date_found = True

                        if editdistance.eval(word[4], "Formation") <=4  and not formation_found:
                            page_bboxes["Stimulated Formation"] = ','.join(stim_page.get_textbox(Rect(Point(word[0] - 50, word[1]), Point(word[0] + 100, word[1] + 20))).split())
                            formation_found = True

                        if editdistance.eval(word[4], "Top") <=1  and not top_found:
                            page_bboxes["Top"] = ','.join(stim_page.get_textbox(Rect(Point(word[0] - 5, word[1]), Point(word[0] + 30, word[1] + 20))).split())
                            top_found = True

                        if editdistance.eval(word[4], "Bottom") <=2  and not bot_found:
                            page_bboxes["Bottom"] = ','.join(stim_page.get_textbox(Rect(Point(word[0], word[1]), Point(word[0] + 40, word[1] + 20))).split())
                            bot_found = True

                        if editdistance.eval(word[4], "Stages") <=2  and not stages_found:
                            page_bboxes["Stages"] = ','.join(stim_page.get_textbox(Rect(Point(word[0]-40, word[1]), Point(word[0]+20, word[1] + 20))).split())
                            stages_found = True

                        if editdistance.eval(word[4], "Volume") <=2  and not volume_found:
                            page_bboxes["Volume"] = ','.join(stim_page.get_textbox(Rect(Point(word[0], word[1]), Point(word[0]+60, word[1] + 20))).split())
                            volume_found = True

                        if editdistance.eval(word[4], "Units") <=1  and not units_found:
                            page_bboxes["Units"] = ','.join(stim_page.get_textbox(Rect(Point(word[0]-25, word[1]), Point(word[0]+20, word[1] + 20))).split())
                            units_found = True

                        if editdistance.eval(word[4], "Type") <=1  and not type_found:
                            page_bboxes["Type"] = ','.join(stim_page.get_textbox(Rect(Point(word[0], word[1]), Point(word[0]+60, word[1] + 20))).split())
                            type_found = True

                        if editdistance.eval(word[4], "Acid") <=2  and not acid_found:
                            page_bboxes["Acid"] = ','.join(stim_page.get_textbox(Rect(Point(word[0], word[1]), Point(word[0]+60, word[1] + 20))).split())
                            acid_found = True

                        if editdistance.eval(word[4], "Proppant") <=3  and not proppant_found:
                            page_bboxes["Proppant"] = ','.join(stim_page.get_textbox(Rect(Point(word[0]-15, word[1]), Point(word[0]+30, word[1] + 20))).split())
                            proppant_found = True

                        if editdistance.eval(word[4], "Pressure") <=3  and not pressure_found:
                            page_bboxes["Pressure"] = ','.join(stim_page.get_textbox(Rect(Point(word[0]-70, word[1]), Point(word[0]+60, word[1] + 20))).split())
                            pressure_found = True

                        if editdistance.eval(word[4], "Rate") <=1  and not rate_found and word[4] != "Date":
                            page_bboxes["Rate"] = ','.join(stim_page.get_textbox(Rect(Point(word[0]-70, word[1]), Point(word[0]+60, word[1] + 20))).split())
                            rate_found = True

                        if editdistance.eval(word[4], "Details") <=1  and not details_found:
                            page_bboxes["Details"] = ','.join(stim_page.get_textbox(Rect(Point(word[0], word[1]), Point(word[0]+200, word[1] + 60))).split())
                            details_found = True

                        if all_found:
                            break

                            
                    peek = ["Date Stimulated","Details"]
                    # print(page_bboxes[peek])
                    if DEBUG:
                        print("Textbox ########")
                        for p in peek:
                            if p in page_bboxes:
                                date_stim = stim_page.get_textbox(page_bboxes[p])
                                print(date_stim.split())
            except:
                a = 0

            #finding database code
            try:
                stim_page = mupdf[c]
                words_a = stim_page.get_text("words")
                name_found = False
                api_found = False
                for w in words:
                    pattern = r'^\d{2}-\d{3}-\d{5}$'
                    if re.match(pattern, w) and not api_found:
                        page_bboxes["API"] = ','.join(stim_page.get_textbox(Rect(Point(w[0]-20, w[1]), Point(w[0]+130, w[1] + 20))).split())
                        date_stim = stim_page.get_textbox(page_bboxes["API"])
                        api_found = True
                
                last_w = ["","","","","",""]
                for w in words_a:
                    if last_w[4].lower() == "well" and w[4].lower() == "name":
                        if editdistance.eval(w[4], "Name") <=1  and not name_found:
                            page_bboxes["Name"] = ','.join(stim_page.get_textbox(Rect(Point(w[0]-20, w[1]), Point(w[0]+200, w[1] + 20))).split())
                            date_stim = stim_page.get_textbox(page_bboxes["Name"])
                            name_found = True
                    last_w = w
            except:
                a = 0
            c += 1

            output_csv[filename][c] = page_bboxes
            
    d += 1
    if d >= 1:
        break

filtered_csv = {}

key_list = ["Name", "API", "Date Stimulated", "Stimulated Formation", "Top", "Bottom", "Stages", "Volume", "Units", "Type", "Acid", "Proppant", "Pressure", "Rate", "Details"]

for k in output_csv.keys():
    filtered_csv[k] = {}
    for k2 in output_csv[k].keys():
        for key in key_list:
            if key in output_csv[k][k2] and key not in filtered_csv[k]:
                filtered_csv[k][key] = output_csv[k][k2][key]
    for key in key_list:
        if key not in filtered_csv[k]:
            filtered_csv[k][key] = ''

host = "localhost"
user = "root"
database="dsci560_lab5"

conn = mysql.connector.connect(host=host, user=user, password=password, database=database)

cursor = conn.cursor()

# SQL query to create the table
create_table_query = """
CREATE TABLE IF NOT EXISTS welldata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255),
    API VARCHAR(255),
    Date_Stimulated VARCHAR(255),
    Stimulated_Formation VARCHAR(255),
    Top VARCHAR(255),
    Bottom VARCHAR(255),
    Stages VARCHAR(255),
    Volume VARCHAR(255),
    Units VARCHAR(255),
    Type VARCHAR(255),
    Acid VARCHAR(255),
    Proppant VARCHAR(255),
    Pressure VARCHAR(255),
    Rate VARCHAR(255),
    Details VARCHAR(255)
);
"""

# Execute the table creation query
cursor.execute(create_table_query)

# Commit the changes
conn.commit()

for pdf in filtered_csv.keys():
    filtered_csv[pdf]
    insert_query = f"""
        INSERT INTO welldata (Name, API, Date_Stimulated, Stimulated_Formation, Top, Bottom, Stages, Volume, Units, Type, Acid, Proppant, Pressure, Rate, Details)
        VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)
    """
    row = [
            filtered_csv[pdf]["Name"], 
            filtered_csv[pdf]["API"], 
            filtered_csv[pdf]["Date Stimulated"], 
            filtered_csv[pdf]["Stimulated Formation"],
            filtered_csv[pdf]["Top"],
            filtered_csv[pdf]["Bottom"], 
            filtered_csv[pdf]["Stages"], 
            filtered_csv[pdf]["Volume"], 
            filtered_csv[pdf]["Units"],
            filtered_csv[pdf]["Type"],
            filtered_csv[pdf]["Acid"], 
            filtered_csv[pdf]["Proppant"], 
            filtered_csv[pdf]["Pressure"], 
            filtered_csv[pdf]["Rate"],
            filtered_csv[pdf]["Details"]
        ]
    cursor.execute(insert_query, tuple(row))
    conn.commit()