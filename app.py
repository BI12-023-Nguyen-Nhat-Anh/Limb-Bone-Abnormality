import json
import shutil
import requests
import jwt
from flask import Flask, jsonify, render_template, url_for, redirect, request, flash,send_file
from flask_login import login_required, logout_user, LoginManager, current_user, login_user
from function.connect import db
from function.models import User,Folder,File
from werkzeug.security import generate_password_hash, check_password_hash
import os
import pandas as pd
import subprocess
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a secrect key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Account.db'
folder_data_dir = '../folder_data'
source_file_path="script.sh"
upload_file_dir="upload_file.sh"
source_dashboard_path='dashboard-script.sh'
jwt_token=''

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def start():
    return redirect(url_for('homepage'))
@app.route('/demo')
def demo():
    return render_template('demo.html')
@app.route('/pipeline')
def pipeline():
    return render_template('pipeline.html')
@app.route('/homepage')
def homepage():
    current_user.role=0
    return render_template('index.html')
@app.route('/ourstory')
def ourstory():
    return render_template('ourstory.html')
@app.route("/aboutus")
def about_us():
    return render_template('about_us.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form["email"]
        users = User.query.filter_by(email = email).first()
        if users:
            return redirect(url_for('reset_password', email=email))
        else:
            flash("The email does not match", category= 'error')
            return render_template('forgot.html')
    
    return render_template('forgot.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        url = "http://user.ulake.usth.edu.vn/api/auth/login"
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        payload = {
            'userName': username,
            'password': password
        }
            
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password) and response.ok:
                flash('Logged in successfully!', category='success')
                data = response.json()
                jwt_token = data['resp']
                token = decode_jwt(jwt_token)
                auth = token['groups']
                user.token = jwt_token
                user.id = token['sub']
                db.session.commit()
                if "Admin" in auth:
                    login_user(user, remember=False)
                    return redirect(url_for("admin"))
                elif "User" in auth:
                    login_user(user, remember=False)
                    return redirect(url_for("home"))
            else:
                flash('Incorrect password! Try again!', category='error')
        else:
            flash('User does not exist!', category='error')
    return render_template("login.html")

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        re_password = request.form.get('re-password')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(username) < 2:
            flash('Username must be greater than 1 character', category='error')
        elif password != re_password:
            flash('Passwords do not match!', category='error')
        elif len(password) < 5:
            flash('Password must be greater than 5 characters', category='error')
        else:
            folder_path = f"{folder_data_dir}/{username}"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                destination_folder_path=folder_path
                copy_and_paste_file(source_file_path, destination_folder_path)
                copy_and_paste_file(source_dashboard_path, destination_folder_path)
            new_user = User(
                email=email,
                username=username,
                password=generate_password_hash(password, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()
           
            flash('Sign up successful!', category='success')
            return redirect(url_for('login'))
    return render_template('sign_up.html')

@app.route('/home')
@login_required
def home():
    folders = Folder.query.filter_by(user_id=current_user.id).all()
    
    return render_template("home.html", folders = folders, user = json_user())

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Log out success")
    return redirect(url_for('homepage'))

@app.route('/folder', methods = ['POST'])
@login_required
def folder():
    if 'folderName' in request.form:
        folder_name = request.form['folderName']

        if folder_name == '':
            flash('No folder name provied!', category= 'error')
        else:
            folder_path = f"{folder_data_dir}/{current_user.username}/{folder_name}"
            folder=Folder.query.filter_by(path=folder_path).first()
            if folder==None:
                url = "http://dashboard.ulake.usth.edu.vn/api/folder"
                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization': f"Bearer {current_user.token}"
                }
                payload = {
                    'name': folder_name
                }
                
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                data = response.json()
                folder_data = data['resp']
                if response.status_code == 200:
                    # Add folder to database
                    new_folder = Folder(id=folder_data['id'],path = folder_path,name= folder_name, user_id = current_user.id)
                    db.session.add(new_folder)
                    db.session.commit()
                    flash("Folder create successfully", category= 'success')
            else:
                flash("Folder already exists",category='error')
    return redirect(url_for('home'))

@app.route('/folder/<folder_id>', methods=['GET', 'POST'])
@login_required
def get_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    file = File.query.filter_by(folder_id=folder.id).first()
    
    path=f"{folder_data_dir}/{current_user.username}"
    folder_path = f"{path}/{folder.name}"
    
    if request.method == "POST":
        if 'inputFile1' in request.files:
            sub_file = request.files['inputFile1']
            if sub_file.filename != '':
                file_name=f"{folder.name}_1.fastq.gz"
                command = upload_file(folder, file_name)
                response = subprocess.run(command, shell=True, check=True, capture_output=True)
                
                stdout_str = response.stdout.decode()
                json_pattern = re.compile(r'\{.*\}')
                json_match = json_pattern.search(stdout_str)
                if json_match:
                    json_line = json_match.group(0)
                    output_data = json.loads(json_line)
                    resp = output_data.get('resp', {})
                    file_id = resp.get('id')
                                    
                new_file = File(id=file_id,name=file_name, path=f"{path}/{file_name}", user_id=current_user.id, folder_id=folder_id)
                db.session.add(new_file)
                db.session.commit()
                sub_file.save(f"{path}/{file_name}")

        if 'inputFile2' in request.files:
            sub_file = request.files['inputFile2']
            
            if sub_file.filename != '':
                file_name=f"{folder.name}_2.fastq.gz"
                command = upload_file(folder, file_name)
                response = subprocess.run(command, shell=True, check=True, capture_output=True)

                file_name=f"{folder.name}_2.fastq.gz"
                stdout_str = response.stdout.decode()
                json_pattern = re.compile(r'\{.*\}')
                json_match = json_pattern.search(stdout_str)
                if json_match:
                    json_line = json_match.group(0)
                    output_data = json.loads(json_line)
                    resp = output_data.get('resp', {})
                    file_id = resp.get('id')
                                
                new_file = File(id=file_id,name=file_name, path=f"{path}/{file_name}", user_id=current_user.id, folder_id=folder_id)
                db.session.add(new_file)
                db.session.commit()
                sub_file.save(f"{path}/{file_name}")

    if not os.path.exists(f"{folder_path}_1.paired_fastqc.html"):
        if os.path.exists(f"{folder_path}_1_fastqc.html"):
            file=File.query.filter_by(name=f"{folder.name}_1_fastqc.html").first()
            if file==None:
                response = subprocess.run(upload_file(folder, f"{folder.name}_1_fastqc.html"), shell=True, check=True, capture_output=True)
                
                file_name=f"{folder.name}_1_fastqc.html"
                stdout_str = response.stdout.decode()
                json_pattern = re.compile(r'\{.*\}')
                json_match = json_pattern.search(stdout_str)
                if json_match:
                    json_line = json_match.group(0)
                    output_data = json.loads(json_line)
                    resp = output_data.get('resp', {})
                    file_id = resp.get('id')

                output_file_path1=f"{folder_path}_1_fastqc.html"
                new_file = File(id=file_id,name=f"{folder.name}_1_fastqc.html", path=output_file_path1, user_id=current_user.id, folder_id=folder_id)
                db.session.add(new_file)
                db.session.commit()
    else:
        file=File.query.filter_by(name=f"{folder.name}_1_fastqc.html").first()
        print(file)
        file_paired=File.query.filter_by(name=f"{folder.name}_1.paired_fastqc.html").first()
        if file!=None:
            url = f"http://folder.ulake.usth.edu.vn/api/file/{file.id}"
            headers = {
                'accept': "*/*",
                'Authorization': f"Bearer {current_user.token}"
            }
            response = requests.delete(url, headers=headers)
            print(f"html: {response}")
            
            if response.status_code == 200:   
                response = subprocess.run(upload_file(folder, f"{folder.name}_1.paired_fastqc.html"), shell=True, check=True, capture_output=True)
                file_name=f"{folder.name}_1.paired_fastqc.html"
                stdout_str = response.stdout.decode()
                json_pattern = re.compile(r'\{.*\}')
                json_match = json_pattern.search(stdout_str)
                if json_match:
                    json_line = json_match.group(0)
                    output_data = json.loads(json_line)
                    resp = output_data.get('resp', {})
                    file_id = resp.get('id')
                
                file.path=f"{folder_path}_1.paired_fastqc.html"
                file.name=f"{folder.name}_1.paired_fastqc.html"
                file.id=file_id
                db.session.add(file)
                db.session.commit()
        elif file_paired==None:
            response = subprocess.run(upload_file(folder, f"{folder.name}_1.paired_fastqc.html"), shell=True, check=True, capture_output=True)
            
            file_name=f"{folder.name}_1.paired_fastqc.html"
            stdout_str = response.stdout.decode()
            json_pattern = re.compile(r'\{.*\}')
            json_match = json_pattern.search(stdout_str)
            if json_match:
                json_line = json_match.group(0)
                output_data = json.loads(json_line)
                resp = output_data.get('resp', {})
                file_id = resp.get('id')         
            
            output_file_path1=f"{folder_path}_1.paired_fastqc.html"
            new_file = File(id=file_id,name=f"{folder.name}_1.paired_fastqc.html", path=output_file_path1, user_id=current_user.id, folder_id=folder_id)
            db.session.add(new_file)
            db.session.commit()
            
    if os.path.exists(f"{folder_path}_1.paired.fastq"):
        file=File.query.filter_by(name=f"{folder.name}_1.paired.fastq").first()
        file_uncheck = File.query.filter_by(name=f"{folder.name}_1.fastq.gz").first()
        if file==None:
            url = f"http://folder.ulake.usth.edu.vn/api/file/{file_uncheck.id}"
            headers = {
                'accept': "*/*",
                'Authorization': f"Bearer {current_user.token}"
            }
            
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                response = subprocess.run(upload_file(folder, f"{folder.name}_1.paired.fastq"), shell=True, check=True, capture_output=True)
                
                file_name=f"{folder.name}_1.paired.fastq"
                stdout_str = response.stdout.decode()
                json_pattern = re.compile(r'\{.*\}')
                json_match = json_pattern.search(stdout_str)
                if json_match:
                    json_line = json_match.group(0)
                    output_data = json.loads(json_line)
                    resp = output_data.get('resp', {})
                    file_id = resp.get('id')
                
                output_file_path1=f"{folder_path}_1.paired.fastq"
                new_file = File(id=file_id,name=f"{folder.name}_1.paired.fastq", path=output_file_path1, user_id=current_user.id, folder_id=folder_id)
                db.session.add(new_file)
                db.session.commit()
                
    if not os.path.exists(f"{folder_path}_2.paired_fastqc.html"):
        if os.path.exists(f"{folder_path}_2_fastqc.html"):
            file=File.query.filter_by(name=f"{folder.name}_2_fastqc.html").first()
            if file==None:
                response = subprocess.run(upload_file(folder, f"{folder.name}_2_fastqc.html"), shell=True, check=True, capture_output=True)
                
                file_name=f"{folder.name}_2_fastqc.html"
                stdout_str = response.stdout.decode()
                json_pattern = re.compile(r'\{.*\}')
                json_match = json_pattern.search(stdout_str)
                if json_match:
                    json_line = json_match.group(0)
                    output_data = json.loads(json_line)
                    resp = output_data.get('resp', {})
                    file_id = resp.get('id')
                
                output_file_path1=f"{folder_path}_2_fastqc.html"
                new_file = File(id=file_id,name=f"{folder.name}_2_fastqc.html", path=output_file_path1, user_id=current_user.id, folder_id=folder_id)
                db.session.add(new_file)
                db.session.commit()
    else:
        file=File.query.filter_by(name=f"{folder.name}_2_fastqc.html").first()
        file_paired=File.query.filter_by(name=f"{folder.name}_2.paired_fastqc.html").first()
        if file!=None:
            url = f"http://folder.ulake.usth.edu.vn/api/file/{file.id}"
            headers = {
                'accept': "*/*",
                'Authorization': f"Bearer {current_user.token}"
            }
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:   
                response = subprocess.run(upload_file(folder, f"{folder.name}_2.paired_fastqc.html"), shell=True, check=True, capture_output=True)
                
                file_name=f"{folder.name}_2.paired_fastqc.html"
                stdout_str = response.stdout.decode()
                json_pattern = re.compile(r'\{.*\}')
                json_match = json_pattern.search(stdout_str)
                if json_match:
                    json_line = json_match.group(0)
                    output_data = json.loads(json_line)
                    resp = output_data.get('resp', {})
                    file_id = resp.get('id')
                
                file.path=f"{folder_path}_2.paired_fastqc.html"
                file.name=f"{folder.name}_2.paired_fastqc.html"
                file.id=file_id
                db.session.add(file)
                db.session.commit()
        elif file_paired==None:
            response = subprocess.run(upload_file(folder, f"{folder.name}_2.paired_fastqc.html"), shell=True, check=True, capture_output=True)
            
            file_name=f"{folder.name}_2.paired_fastqc.html"
            stdout_str = response.stdout.decode()
            json_pattern = re.compile(r'\{.*\}')
            json_match = json_pattern.search(stdout_str)
            if json_match:
                json_line = json_match.group(0)
                output_data = json.loads(json_line)
                resp = output_data.get('resp', {})
                file_id = resp.get('id')         
            
            output_file_path1=f"{folder_path}_2.paired_fastqc.html"
            new_file = File(id=file_id,name=f"{folder.name}_2.paired_fastqc.html", path=output_file_path1, user_id=current_user.id, folder_id=folder_id)
            db.session.add(new_file)
            db.session.commit()
                
    if os.path.exists(f"{folder_path}_2.paired.fastq"):
        file=File.query.filter_by(name=f"{folder.name}_2.paired.fastq").first()
        file_uncheck = File.query.filter_by(name=f"{folder.name}_2.fastq.gz").first()
        if file==None:
            url = f"http://folder.ulake.usth.edu.vn/api/file/{file_uncheck.id}"
            headers = {
                'accept': "*/*",
                'Authorization': f"Bearer {current_user.token}"
            }
            
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                response = subprocess.run(upload_file(folder, f"{folder.name}_2.paired.fastq"), shell=True, check=True, capture_output=True)
                
                file_name=f"{folder.name}_2.paired.fastq"
                stdout_str = response.stdout.decode()
                json_pattern = re.compile(r'\{.*\}')
                json_match = json_pattern.search(stdout_str)
                if json_match:
                    json_line = json_match.group(0)
                    output_data = json.loads(json_line)
                    resp = output_data.get('resp', {})
                    file_id = resp.get('id')
                
                output_file_path1=f"{folder_path}_2.paired.fastq"
                new_file = File(id=file_id,name=f"{folder.name}_2.paired.fastq", path=output_file_path1, user_id=current_user.id, folder_id=folder_id)
                db.session.add(new_file)
                db.session.commit()

    if os.path.exists(f"{folder_path}.indels.hg38_multianno.csv"):
        file=File.query.filter_by(name=f"{folder.name}.indels.hg38_multianno.csv").first()
        if not file:
            output_file_path1=f"{folder_path}.indels.hg38_multianno.csv"
            command = upload_file(folder, f"{folder.name}.indels.hg38_multianno.csv")
            response = subprocess.run(command, shell=True, check=True, capture_output=True)
            
            file_name=f"{folder.name}.indels.hg38_multianno.csv"
            stdout_str = response.stdout.decode()
            json_pattern = re.compile(r'\{.*\}')
            json_match = json_pattern.search(stdout_str)
            if json_match:
                json_line = json_match.group(0)
                output_data = json.loads(json_line)
                resp = output_data.get('resp', {})
                file_id = resp.get('id')
            
            new_file = File(id=file_id, name=f"{folder.name}.indels.hg38_multianno.csv", path=output_file_path1, user_id=current_user.id, folder_id=folder_id)
            db.session.add(new_file)
            db.session.commit()
    
    if os.path.exists(f"{folder_path}.SNPs.hg38_multianno.csv"):
        file=File.query.filter_by(name=f"{folder.name}.SNPs.hg38_multianno.csv").first()
        if not file:
            output_file_path2=f"{folder_path}.SNPs.hg38_multianno.csv"
            command = upload_file(folder, f"{folder.name}.SNPs.hg38_multianno.csv")
            response = subprocess.run(command, shell=True, check=True, capture_output=True)
            
            file_name=f"{folder.name}.SNPs.hg38_multianno.csv"
            stdout_str = response.stdout.decode()
            json_pattern = re.compile(r'\{.*\}')
            json_match = json_pattern.search(stdout_str)
            if json_match:
                json_line = json_match.group(0)
                output_data = json.loads(json_line)
                resp = output_data.get('resp', {})
                file_id = resp.get('id')
            
            new_file = File(id=file_id, name=f"{folder.name}.SNPs.hg38_multianno.csv", path=output_file_path2, user_id=current_user.id, folder_id=folder_id)
            db.session.add(new_file)
            db.session.commit()
        
    subfolders = Folder.query.filter_by(parent_folder_id=folder.id).all()
    subfiles = File.query.filter_by(folder_id=folder.id).all()
    output=[]
    files=[]
    for file in subfiles:
        if file.name.endswith(".csv") or file.name.endswith(".html"):
            output.append(file)
        else:
            files.append(file)
    return render_template('folder.html', folder=folder, subfolders=subfolders, file = file, subfiles = files, output=output, user = current_user)

@app.route('/file/<file_id>', methods = ['GET', 'POST'])
@login_required
def get_file(file_id):
    file = File.query.get_or_404(file_id)
    file_path = file.path

    if file.name.endswith('csv'):
        df = pd.read_csv(file_path)
        if request.method == 'POST':
            # Take requests from form
            selected_columns = request.form.getlist('columns')
            
            # Create dataframe for all the columns chosen
            selected_df = df[selected_columns]
            temp_file_path = f"{folder_data_dir}/{current_user.username}/temp_selected_data.csv"
            selected_df.to_csv(temp_file_path, index=False)

            # Extract column titles and data for the template
            columns = selected_df.columns.tolist()
            rows = selected_df.values.tolist()

            # Send data to user
            return render_template('display_columns.html', columns=columns, rows=rows, user=current_user, file=file)
    
    elif file.name.endswith('html'):
        return send_file(file.path, mimetype='text/html')
    
    return render_template('select_columns.html', columns=df.columns,user = current_user)
    
@app.route('/delete-subfile', methods=['POST'])
@login_required
def delete_subfile():
    try:
        event = json.loads(request.data)
        file_id = event['Id']

        file = File.query.filter_by(id=file_id, user_id=current_user.id).first()

        url = f"http://folder.ulake.usth.edu.vn/api/file/{file_id}"
        headers = {
            'accept': "*/*",
            'Authorization': f"Bearer {current_user.token}"
        }
        
        response = requests.delete(url, headers=headers)
        print(response)
        if file and response.status_code==200:
            if file.user_id == current_user.id:
                folder = Folder.query.get(file.folder_id)
                if folder and is_file_in_folder(file, folder):
                    file_to_delete = file.path
                    if os.path.exists(file_to_delete):
                        os.remove(file_to_delete)
                        flash('File deleted from folder successfully',category='success')
                        db.session.delete(file)
                        db.session.commit()
                    else:
                        flash('File not found in folder',category='error')
                else:
                    flash('File not found in folder',category='error')
            else:
                flash('You do not have permission to delete this file',category='error')
        else:
            raise ValueError('File not found')

        return jsonify({})
    except Exception as e:
        flash(f"Error deleting file: {e}",category='error')
        return jsonify({'Status': 'Error occurred while deleting the file.'}), 500
    
@app.route('/delete-folder', methods=['POST'])
@login_required
def delete_folder():
    try:
        event = json.loads(request.data)
        folder_id = event['Id']
        
        url = f"http://dashboard.ulake.usth.edu.vn/api/folder/{folder_id}"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {current_user.token}"
        }
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            delete_folder_recursive(folder_id)
            flash('Delete successfully',category='success')
        return jsonify({'Status':'Success to delete folder'})
    except Exception as e:
        flash(f"Error deleting folder: {e}",category='error')
        return jsonify({'Status': 'Error occurred while deleting the folder.'}), 500

@app.route('/download/<file_id>',methods=['GET'])
@login_required
def download_file(file_id):
    return send_file(path_or_file=f"{folder_data_dir}/{current_user.username}/temp_selected_data.csv", as_attachment=True, mimetype="text/csv")
    
@app.route('/execute', methods = ['POST'])
@login_required
def execute_fatsq():
    from executing import execute_file
    event=json.loads(request.data)
    id=event['Id']
    selectedOption=event['selectedOptions']
    folder=Folder.query.filter_by(id = id).first()
    try:
        execute_file(folder, current_user, selectedOption)
        return jsonify({"Status":"True"})
    except:
        return jsonify({"Status":"False"})

# Admin
@app.route('/admin', methods=['POST','GET'])
@login_required
def admin():
    # admin=User.query.filter(User.role!=1).all()
    
    return render_template("admin.html", current_user=json_user())

@app.route('/create_user',methods=['POST','GET'])
@login_required
def create_user():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        lastname = request.form.get('last_name')
        firstname = request.form.get('first_name')
        password = request.form.get('password')
        re_password = request.form.get('re-password')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(username) < 2:
            flash('Username must be greater than 1 character', category='error')
        elif password != re_password:
            flash('Passwords do not match!', category='error')
        elif len(password) < 5:
            flash('Password must be greater than 5 characters', category='error')
        else:
            folder_path = f"{folder_data_dir}/{username}"
            
            response = add_new_user(username, firstname, lastname, email, password)
            
            data = response.json()
            resp = data['resp']
            user_id = resp['id']
            if response.status_code == 200:            
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    destination_folder_path=folder_path
                    copy_and_paste_file(source_file_path, destination_folder_path)
                new_user = User(
                    id=user_id,
                    email=email,
                    username=username,
                    password=generate_password_hash(password, method='pbkdf2:sha256')
                )
                db.session.add(new_user)
                db.session.commit()

        return redirect(url_for('admin'))

    return render_template('add_user.html', user=current_user)

def json_user():
    user_json = {
        'id': current_user.id,
        'username': current_user.username,
        'token': current_user.token,
        'role': current_user.role
    }
    return user_json

def add_new_user(username, firstname, lastname, email, password):
    url = "http://user.ulake.usth.edu.vn/api/user"
    payload = {
        "userName": username,
        "firstName": firstname,
        "lastName": lastname,
        "isAdmin": False,
        "email": email,
        "password": password,
        "registerTime": 0,
        "status": True,
        "code": "yourCode",
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response

def decode_jwt(jwt_code):
    return jwt.decode(jwt_code, options={"verify_signature": False}) 

def is_file_in_folder(file, folder):
    # Check if the file's folder matches the specified folder or any of its subfolders
    if file.folder_id == folder.id:
        return True
    elif folder.subfolders:
        for subfolder in folder.subfolders:
            if is_file_in_folder(file, subfolder):
                return True
    return False

def delete_folder_recursive(folder_id):
    folder = Folder.query.filter_by(id=folder_id).first()
    if folder is None:
        return jsonify({"Status":"Fail"})

    # Delete files in the current folder
    delete_files_in_folder(folder.id)

    # Delete the current folder
    db.session.delete(folder)
    db.session.commit()

def delete_files_in_folder(folder_id):
    files = File.query.filter_by(folder_id=folder_id).all()
    for file in files:
        os.remove(file.path)
        db.session.delete(file)
    db.session.commit()

def upload_file(folder, file_name):
    command = f"bash {upload_file_dir} {current_user.token} {file_name} {current_user.id} {folder.id} {folder.name}"
    return command

def copy_and_paste_file(source_file, destination_folder):
    try:
        if os.path.isfile(source_file):
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)

            # create full path to the right dictionary 
            destination_path = f"{destination_folder}/{os.path.basename(source_file)}"

            # Paste to the folder path
            shutil.copy2(source_file, destination_path)

            print("Create file successfully")
        else:
            print("Fail to create a file")
    except Exception as e:
        print(f"Error: {e}")    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
