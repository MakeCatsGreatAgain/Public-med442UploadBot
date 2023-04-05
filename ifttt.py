import requests
from urllib import request
import subprocess  
from pathlib import Path
import os
import re

#Setup path of drive 
batch = ""
year = ""
block = ""
folder = ""
gender = ""
#Url
ifttt_url = ""

def setup_442():
    global batch
    global year
    global block
    global folder
    global ifttt_url
    batch = "Med442"
    year = "2nd Year"
    block = "2.GNT"
    folder = "Slides"
    ifttt_url = "https://maker.ifttt.com/trigger/[IFTTT EVENT NAME]/with/key/[IFTTT API CODE]"

def setup_443():
    global batch
    global year
    global block
    global folder
    global ifttt_url
    batch = ""
    year = "1st Year"
    block = "2.MSK Block"
    folder = "Slides"
    ifttt_url = "https://maker.ifttt.com/trigger/[IFTTT EVENT NAME]/with/key/[IFTTT API CODE]"


def upload(path, filename,subject, lecture, batch, female):
    print("HAHAH: " + path)
    if batch == 442: setup_442()
    elif batch == 443: setup_443()
    global gender
    if(female): gender = "Female"
    else: gender = "Male"
    gd_path = google_drive_path(subject, filename)
    print(f"GD_PATH:{gd_path}")
    upload_catbox(path, lecture, gd_path)
    if(path.endswith(".pdf") == False):
        pdf_path = convert_to_pdf(filename)
        print(pdf_path)
        upload_catbox(pdf_path, lecture, gd_path)


def convert_to_pdf(filename):
    print("NOW MAKE IT PDF")
    folder_path = f"./downloadedpttx/{filename}" 
    static_path = f"./med442pdf/" 
    cmd_command = ("libreoffice --headless --convert-to pdf --outdir " + static_path + " --convert-to pdf \"" + folder_path + "\"")
    proc=subprocess.Popen( cmd_command, shell=True) 
    proc.communicate()
    pre, ext = os.path.splitext(filename)
    return f"./med442pdf/{pre}.pdf"

def setupPBL(filename):
    print(filename)
    case = re.search("Case [\d][f]*", filename)
    try:
        print(f"CASE IS: {case.group()}")
        return case.group().replace("f", "").title()
    except AttributeError:
        return "Unknown"

def google_drive_path(subject, filename):
    if(subject == "familymedicine"): subject = "Family medicine"
    if(subject == "cardiacsciences"): subject = "Cardiac science"
    if(subject == "ospe_physiology"): subject = "(OSPE)/Physiology"
    if(subject == "ospe_anatomy"): subject = "(OSPE)/Anatomy"
    if(subject == "ospe_pathology"): subject = "(OSPE)/Pathology"
    if(subject == "ospe_histology"): subject = "(OSPE)/Histology"
    if(subject == "ospe_radiology"): subject = "(OSPE)/Radiology"
    else: subject = subject.title()
    folder_path = batch + "/" + year + "/" + block + "/" + subject + "/" +  folder + "/" +  gender
    print(folder_path)
    if(subject == "Pbl"):
        case = setupPBL(filename) 
        subject = f"( PBL )/{case}/"
    print(f"WE GONNA WIN BIG: {folder_path}")
    return folder_path



def upload_catbox(path, lecture, gd_path):
    filename, file_extension = os.path.splitext(path)
    print(f"THA PATH IS: {path}")
    print(f"THA gd_path IS: {gd_path}")
    print(f"THA filename IS: {filename}")
    print(f"THA file_extension IS: {file_extension}")
    files = {
        'reqtype': (None, 'fileupload'),
        'time': (None, '1h'),
        'fileToUpload': (path, open(path, 'rb')),
    }
    response = requests.post('https://litterbox.catbox.moe/resources/internals/api.php', files=files)
    print("URL IS: " + str(response.content))
    #URL/NAME/PATH
    param = {"value1":  str(response.content), "value2": f"{lecture}{file_extension}", "value3" : gd_path}
    ifttt_request =  requests.post(ifttt_url, params=param)


