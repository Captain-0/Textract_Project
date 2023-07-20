import csv

from flask import Flask, render_template, request, send_file, session, redirect
from werkzeug.utils import secure_filename
import os
import fitz  # this is pymupdf
import spacy

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'saved_file'
nlp = spacy.load("en_core_web_sm")


@app.route('/')
def home():
    return render_template("upload_form.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Here you should save the file
            file.save(f'C:\\Users\\1\\Documents\\Textract Project\\saved_file\\{filename}.pdf')
            with fitz.open(f"C:\\Users\\1\\Documents\\Textract Project\\saved_file\\{filename}.pdf") as doc:
                text = [anotherelement["text"] for page in doc
                        for item in page.get_text("dict")["blocks"]
                        for element in item["lines"]
                        for anotherelement in element["spans"]]
                text = [item for item in text if len(item) > 1]
            file_location = f'/saved_file/{filename}'

            result = {}
            doc = nlp("".join(text))
            for ent in doc.ents:
                print(f"{ent.label_} = {ent.text}")
                result[ent.label_] = ent.text
            print(result)
            send_file(f'C:\\Users\\1\\Documents\\Textract Project\\saved_file\\{filename}.pdf', as_attachment=False)

            return render_template("display_page.html", filename=file_location, dictionary=result)

    return 'File upload failed'


# def handle_submit():
#     # request.form.get('name') == 'main_form':
#     print("below is form data")
#     print(request.form)
#         # session["for_data"] = request.form
#         # print(session.get("for_data"))
#     return download_csv()
#     # else:
#     #     return 'Invalid form submission'


def convert_to_csv(form_data):
    print("form data from convert to csv")
    print(form_data)
    data = [{'key': key, 'value': value} for key, value in form_data.items()]
    print(data)
    fieldnames = ['key', 'value']

    csv_filename = 'data.csv'
    csv_filepath = os.path.join(app.root_path, 'static', csv_filename)

    with open(csv_filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    return csv_filepath


@app.route('/download', methods=['GET', 'POST'])
def download_csv():
    csv_filepath = convert_to_csv(request.form)
    return send_file(csv_filepath, as_attachment=True, download_name='data.csv')




ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(debug=True)
