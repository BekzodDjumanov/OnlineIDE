from flask import Flask, render_template, request, jsonify, redirect, url_for
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('python_ide'))

# for Python IDE
@app.route('/python')
def python_ide():
    return render_template('index.html')

# for Serve Java IDE
@app.route('/java')
def java_ide():
    return render_template('java.html')

# for runner for both
@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get('code')
    language = data.get('language', 'python')

    if not code:
        return jsonify({'output': 'No code provided.'}), 400

    if language == 'java':
        return run_java(code)
    else:
        return run_python(code)

def run_python(code):
    try:
        result = subprocess.run(
            ['python3', '-c', code],
            capture_output=True,
            text=True,
            timeout=5
        )
        return jsonify({'output': result.stdout or result.stderr})
    except subprocess.TimeoutExpired:
        return jsonify({'output': 'Execution timed out.'})
    except Exception as e:
        return jsonify({'output': f'Error: {str(e)}'}), 500

def run_java(code):
    try:
        filename = "Main"
        java_file = f"{filename}.java"

        with open(java_file, 'w') as f:
            f.write(code)

        compile = subprocess.run(['javac', java_file], capture_output=True, text=True, timeout=10)
        if compile.returncode != 0:
            return jsonify({'output': compile.stderr})

        run = subprocess.run(['java', filename], capture_output=True, text=True, timeout=10)
        output = run.stdout if run.stdout else run.stderr

        os.remove(java_file)
        os.remove(f"{filename}.class")

        return jsonify({'output': output})
    except subprocess.TimeoutExpired:
        return jsonify({'output': 'Execution timed out.'})
    except Exception as e:
        return jsonify({'output': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False)