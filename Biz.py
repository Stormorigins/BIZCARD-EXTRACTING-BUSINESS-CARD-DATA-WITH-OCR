#LIBRARIES

import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import re
from PIL import Image
import pandas as pd 
import numpy as np
import pymysql
import io

#FUNCTION TO CONVERT IMAGE TO  TXT

def IMG_to_TXT(path):
    Inp_Img= Image.open(path)
    Img_arr= np.array(Inp_Img)# converting image into array
    lang= easyocr.Reader(["en"]) #define reader language 
    text= lang.readtext(Img_arr, detail=0)
    return text, Inp_Img

#FUNCTION TO EXTRACT TXT FROM IMAGE

def TXT_EXTRACT(text):

    list={"NAME":[],"DESIGNATION": [],"COMPANY_NAME":[],"CONTACT":[],"EMAIL_ID":[],"WEBSITE":[],"ADDRESS":[],"PINCODE":[]}

    list["NAME"].append(text[0])
    list["DESIGNATION"].append(text[1])
    for i in range(2,len(text)):
        if text[i].startswith("+") or (text[i].replace("-","").isdigit() and "-" in text[i]):
            list["CONTACT"].append(text[i])
        elif "@" in text[i] and (text[i].endswith(".com")):
            list["EMAIL_ID"].append(text[i])
        elif "WWW" in text[i] or "www" in text[i] or "Www" in text[i] or "wWw" in text[i] or "wwW" in text[i]:
            web=text[i].lower()
            list["WEBSITE"].append(web)
        # elif "@" not in text[i] and (text[i].endswith(".com")):
        #     list["WEBSITE"].append(text[i])
        elif "TamilNadu" in text[i] or "Tamil Nadu" in text[i] or text[i].isdigit():
            list["PINCODE"].append(text[i])
        elif re.match (r'^[A-Z,a-z]',text[i]):
            list["COMPANY_NAME"].append(text[i])
        else:
            remove= re.sub(r'^[,;]','',text[i])
            list["ADDRESS"].append(remove)
    
    for key, value in list.items():
        if len(value)>0:
            concate= " ".join(value)
            list[key]=[concate]
        else:
            value= "NA"
            list[key]=[value]


    return list



#STREAMLIT PART

#PAGE LAYOUT

st.set_page_config(page_title="Bizcard",page_icon="🌍",layout="wide",initial_sidebar_state="expanded")
# page_bg_img='''<style>[data-testid="stAppViewContainer"]{background-color:#FFFFF;}</style>'''
# st.markdown(page_bg_img,unsafe_allow_html=True)

# st.markdown(f""" <style>.stApp {{
#                         background:url("https://wallpapers.com/images/featured/plain-zoom-background-d3zz0xne0jlqiepg.jpg");
#                         background-size: cover}}
#                      </style>""", unsafe_allow_html=True)

#TITLE
st.write("""<p style="font-family:Cursive, Lucida Handwriting;font-size: 45px; text-align: center; color:#FFFFF ">
         BizCardX: Extracting Business Card Data with OCR</p>""", unsafe_allow_html=True)


#MENU BAR
col1,col2,col3= st.columns([1,4,1])
with col2:    
    SELECT = option_menu(menu_title=None,options = ["Home","Upload & Modifying","Delete"],icons =["house","upload","delete"],
        default_index=0,orientation="horizontal",styles={"container": {"background-size":"auto", "width": "100%"},
        "icon": {"color": "black", "font-size": "20px"},"nav-link": {"font-size": "15px","font-family":"Cursive, Lucida Handwriting", 
        "text-align": "center", "margin": "0px", "--hover-color": "#FF7F50"},
        "nav-link-selected": {"background-color": "#85C1E9"}})


if SELECT== "Home":
    col1,col2,col3= st.columns(3)
    with col2:

        st.image(Image.open(r"C:\Users\Aishwarya MMPL\Documents\GUVI_PYTHON\Projects\bizcard\img\11.jpg"), 
                caption=None, width=100, use_column_width=True, clamp=False, channels="RGB", output_format="auto")


    st.write("""<p style="font-family:Cursive, Lucida Handwriting;font-size: 35px; text-align: center">
            Introduction</p>""", unsafe_allow_html=True)

    with st.container(border=False,height=130):
        st.write("""<p style="font-family:Cursive, Lucida Handwriting;font-size: 18px; text-align: left"> BizCardX is a Stream lit web application designed to effortlessly extract data from business cards using Optical Character Recognition (OCR) technology. With BizCardX, users can easily upload images of business cards, and the application leverages the powerful easyOCR library to extract pertinent information from the cards. The extracted data is then presented in a user-friendly format and can be stored in a SQL database for future reference and management..</p>""", unsafe_allow_html=True)
        
    
    st.subheader("About the Application")
    st.write(" Users can save the information extracted from the card image using easy OCR. The information can be uploaded into a database (MySQL) after alterations that supports multiple entries. ")
    st.subheader("What is Easy OCR?")
    st.write("Optical Character Recognition (OCR) is the process that converts an image of text into a machine-readable text format. For example, if you scan a form or a receipt, your computer saves the scan as an image file. You cannot use a text editor to edit, search, or count the words in the image file.")
   
    

elif SELECT=="Upload & Modifying":
    pass
    File= st.file_uploader("Upload the file",type=["png","jpeg","jpg"])#file uploader

    if File is not None:
        st.image(File,width=500)
        Texts,Images = IMG_to_TXT(File)
        TEXDIC= TXT_EXTRACT(Texts)

        if TEXDIC:
            st.success("Data Extracted")
            df= pd.DataFrame(TEXDIC)
            
            #coverting Image into Bits 
            Image_Bytes = io.BytesIO()
            Inp_Img.save(Image_Bytes,format="PNG")
            IMG_DATA= Image_Bytes.getvalue()

            dict= {"IMAGE":[IMG_DATA]}
            df_1=pd.DataFrame(dict)
            JOIN = pd.concat([df,df_1],axis=1)
            st.dataframe(JOIN)

            buttton1=st.button("Save")
            if buttton1:
                #SQL CONNECTION
                myconnection = pymysql.connect(host = '127.0.0.1',user='root',passwd='root',database = "bizcard",port=3306)
                cur = myconnection.cursor()

                Create_Query='''create table if not exists BIZCARD(NAME char(255), DESIGNATION char(255), COMPANY_NAME char(255), CONTACT char(255), 
                                    EMAIL_ID char(255), WEBSITE text, ADDRESS text, PINCODE char(255), IMAGE LONGBLOB)'''

                cur.execute(Create_Query)
                myconnection.commit()

                Insert_Query='''insert into BIZCARD(NAME, DESIGNATION, COMPANY_NAME, CONTACT, EMAIL_ID, WEBSITE, ADDRESS, PINCODE,  IMAGE)
                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

                Values= JOIN.values.tolist()[0]
                cur.execute(Insert_Query,Values)
                myconnection.commit()
                st.success(" Saved successfully ")
        else:
            st.success(" Please Upload correct format ")
    
    Method = st.radio("Select the method",["None","Preview","Modify"])

    if Method == "None":
        pass
    if Method == "Preview":
        #SQL CONNECTION
        myconnection = pymysql.connect(host = '127.0.0.1',user='root',passwd='root',database = "bizcard",port=3306)
        cur = myconnection.cursor()

        #Query 
        cur.execute("select * from bizcard")
        myconnection.commit()
        F1 = cur.fetchall()
        Data= pd.DataFrame(F1, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL_ID", "WEBSITE", "ADDRESS", "PINCODE",  "IMAGE"))
        st.dataframe(Data)
    
    if Method == "Modify":

        #SQL CONNECTION
        myconnection = pymysql.connect(host = '127.0.0.1',user='root',passwd='root',database = "bizcard",port=3306)
        cur = myconnection.cursor()

        #Query 
        cur.execute("select * from bizcard")
        myconnection.commit()
        F1 = cur.fetchall()
        Data= pd.DataFrame(F1, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL_ID", "WEBSITE", "ADDRESS", "PINCODE",  "IMAGE"))

        col1,col2= st.columns(2)
        with col1:
            Name= st.selectbox("select the name",Data["NAME"],index=0)
        DF1= Data[Data["NAME"]==Name]
        st.dataframe(DF1)

        DF2= DF1.copy()

        col1,col2= st.columns(2)
        with col1:
            Edit_Name= st.text_input("Name",DF1["NAME"].unique()[0])
            Edit_Desg= st.text_input("Designation",DF1["DESIGNATION"].unique()[0])
            Edit_Cmp= st.text_input("Company Name",DF1["COMPANY_NAME"].unique()[0])
            Edit_Con= st.text_input("Contact",DF1["CONTACT"].unique()[0])

        DF2["NAME"]=Edit_Name
        DF2["DESIGNATION"]=Edit_Desg
        DF2["COMPANY_NAME"]=Edit_Cmp
        DF2["CONTACT"]=Edit_Con

        with col2:
            Edit_Web= st.text_input("Website",DF1["WEBSITE"].unique()[0])
            Edit_Add= st.text_input("Address",DF1["ADDRESS"].unique()[0])
            Edit_Pin= st.text_input("Pincode",DF1["PINCODE"].unique()[0])
            Edit_Img= st.text_input("Image",DF1["IMAGE"].unique()[0])
        
        DF2["WEBSITE"]=Edit_Web
        DF2["ADDRESS"]=Edit_Add
        DF2["PINCODE"]=Edit_Pin
        DF2["IMAGE"]=Edit_Img

        st.dataframe(DF2)

        button2= st.button("Modify")

        if button2:
            #SQL CONNECTION
            myconnection = pymysql.connect(host = '127.0.0.1',user='root',passwd='root',database = "bizcard",port=3306)
            cur = myconnection.cursor()

            #Query 
            cur.execute(f"delete from BIZCARD where NAME='{Name}'")
            myconnection.commit()

            Insert_Query='''insert into BIZCARD(NAME, DESIGNATION, COMPANY_NAME, CONTACT, EMAIL_ID, WEBSITE, ADDRESS, PINCODE,  IMAGE)
                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

            Values= DF2.values.tolist()[0]
            cur.execute(Insert_Query,Values)
            myconnection.commit()
            st.success(" Modified successfully ")


elif SELECT=="Delete":
    pass
    #SQL CONNECTION
    myconnection = pymysql.connect(host = '127.0.0.1',user='root',passwd='root',database = "bizcard",port=3306)
    cur = myconnection.cursor()

    col1,col2= st.columns(2)
    with col1:
        cur.execute("select NAME from bizcard")
        Table= cur.fetchall()
        myconnection.commit()
        
        Names1=[]
        for i in Table:
            Names1.append(i[0])

        Name= st.selectbox("Select The Name",Names1,index=0)

    with col2:
        cur.execute(f"select DESIGNATION from bizcard where NAME = '{Name}'")
        Table1= cur.fetchall()
        myconnection.commit()
        
        desig1=[]
        for j in Table1:
            desig1.append(j[0])

        desi= st.selectbox("select The Designation",desig1,index=0)

    if Name and desi:
        col1,col2,col3= st.columns(3)
    with col1:
        st.write(f"Selected Name : {Name}")
        # st.write("")
        # st.write("")
        # st.write("")
        st.write(f"Select the Designation : {desi}")
    
    with col3:
        Remove= st.button("Delete",use_container_width=True)
        if Remove:
            cur.execute(f"delete from BIZCARD where NAME='{Name}' and DESIGNATION= '{desi}'")
            myconnection.commit()
            st.warning("DELETED")