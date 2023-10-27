import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, Response
from PyPDF2 import PdfMerger
from PyPDF2 import PdfReader
import json
import PyPDF2
import xml.etree.ElementTree as ET

import openai


load_dotenv()
app = Flask(__name__, template_folder='.')

# Configure OpenAI API key
openai.api_key = os.getenv('API_KEY')


@app.route('/')
def index():
   return render_template('index.html')

@app.route('/inserturl', methods=['POST'])
def inserturl():
    url = request.form['url'] 
    generated_faq = faq(url)
    return render_template('faq.html', questions=generated_faq, url=url)

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfFileReader(uploaded_file)
        pdf_text = ''
        for page in range(pdf_reader.numPages):
            pdf_text += pdf_reader.getPage(page).extractText()

        # Generate questions using OpenAI GPT-3
        generated_questions = generate_questions(pdf_text)
        # Create XML response
        root = ET.Element("question")
        name = ET.SubElement(root, "name")
        name.text = f"here is the question."
        questiontext = ET.SubElement(root, "questiontext", format="html")
        generalfeedback = ET.SubElement(root, "generalfeedback", format="html")
        generalfeedback.text = ET.SubElement(generalfeedback, "text")
        defaultgrade = ET.SubElement(root, "defaultgrade")
        defaultgrade.text = "0"
        penalty = ET.SubElement(root, "penalty")
        penalty.text = "0.3333333"
        hidden = ET.SubElement(root, "hidden")
        hidden.text = "0"
        idnumber = ET.SubElement(root, "idnumber")
        single = ET.SubElement(root, "single")
        single.text = "true"
        shuffleanswers = ET.SubElement(root, "shuffleanswers")
        shuffleanswers.text = "true"
        answernumbering = ET.SubElement(root, "answernumbering")
        answernumbering.text = "abc"
        showstandardinstruction = ET.SubElement(root, "showstandardinstruction")
        showstandardinstruction.text = "0"
        correctfeedback = ET.SubElement(root, "correctfeedback", format="html")
        correctfeedback.text = "Your answer is correct."
        partiallycorrectfeedback = ET.SubElement(root, "partiallycorrectfeedback", format="html")
        partiallycorrectfeedback.text = "Your answer is partially correct."
        incorrectfeedback = ET.SubElement(root, "incorrectfeedback", format="html")
        incorrectfeedback.text = "Your answer is incorrect"

        for i,question in enumerate(generated_questions):
            # question:
            question_elem = ET.SubElement(questiontext, "question")
            question_elem.text = f"<![CDATA[<p dir=\"ltr\" style=\"text-align: left;\">question {question['question'][0]}</p>]]>"

            #  extra item so we are skipping it.
            answer_clean_up = question['question'][-1][8:]

            # everything between the first and the last item. There is a weird /n from the render that cause an extra item so we are skipping it.
            for item in question['question'][1:-2]:
                if answer_clean_up == item:
                    answer_elem = ET.SubElement(question_elem, "answer", format="html")
                    answer_elem.set("fraction", "100")
                    answer_text_elem = ET.SubElement(answer_elem, "text")
                    answer_text_elem.text = f"<![CDATA[<p>{item}</p>]]>"
                else:
                    answer_elem = ET.SubElement(question_elem, "answer", format="html")
                    answer_elem.set("fraction", "0")
                    answer_text_elem = ET.SubElement(answer_elem, "text")
                    answer_text_elem.text = f"<![CDATA[<p>{item}</p>]]>"

        response = ET.tostring(root).decode('utf-8')
        return Response(response, content_type='text/xml')
    return Response('<error>No file selected!</error>', content_type='text/xml')    

def faq(url):
    # Use OpenAI API to generate a faq
    prompt = f"Create a frequenting asked question based on the following url: {url}. Provide the correct answer at the end."
    response = openai.Completion.create(
        engine="text-davinci-003",  # You can use other engines like "text-davinci-002" based on your needs
        prompt=prompt,
        max_tokens=200,  # You can adjust the max tokens based on the desired length of the response
        n=4,  # Number of questions you want to generate
        stop=None
    )
    print(response)
    # Parse OpenAI response and construct multiple-choice questions
    questions = []
    for choice in response.choices:
        question_text = choice['text'].strip().splitlines()
        
        # Construct the question dictionary
        question_dict = {
            "question": question_text,
        }
        
        questions.append(question_dict)
    print(questions)
    return questions

def generate_questions(text):
    # Use OpenAI API to generate multiple-choice questions based on the extracted text
    # https://www.niaid.nih.gov/sites/default/files/score-investigator-responsibilities.pdf
    # prompt = f"Create multiple-choice questions based on the following text: {text}\n\nAnswer each question with the most appropriate choice: A, B, C, or D in a new line.\n\nProvide the correct answer at the end."
    # prompt = f"Create multiple-choice questions based on the following pdf: https://www.niaid.nih.gov/sites/default/files/score-investigator-responsibilities.pdf\n\nAnswer each question with the most appropriate choice: A, B, C, or D in a new line.\n\nProvide the correct answer at the end."
    prompt = f"Create 6 frequenting asked questions based on the following pdf: https://www.niaid.nih.gov/sites/default/files/score-investigator-responsibilities.pdf\n\nProvide the correct answer at the end."
    response = openai.Completion.create(
        engine="text-davinci-003",  # You can use other engines like "text-davinci-002" based on your needs
        prompt=prompt,
        max_tokens=170,  # You can adjust the max tokens based on the desired length of the response
        n=4,  # Number of questions you want to generate
        stop=None
    )
    
    # Parse OpenAI response and construct multiple-choice questions
    questions = []
    for choice in response.choices:
        question_text = choice['text'].strip().splitlines()
        
        # Construct the question dictionary
        question_dict = {
            "question": question_text,
        }
        
        questions.append(question_dict)

    print(response)
    print(question_dict['question'])
    return questions
       
if __name__ == '__main__':
   app.run(debug=True)



