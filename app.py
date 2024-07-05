from flask import Flask, request, jsonify, send_from_directory
import subprocess

app = Flask(__name__)


@app.route('/')
def index():
    return send_from_directory('', 'index.html')


@app.route('/run', methods=['POST'])
def run_poker_agent():
    # Run the poker agent script and capture the output
    result = subprocess.run(['python', 'main.py'], capture_output=True, text=True)

    # Return the output as JSON
    return jsonify({
        'output': result.stdout,
        'error': result.stderr
    })


if __name__ == '__main__':
    app.run(debug=True)