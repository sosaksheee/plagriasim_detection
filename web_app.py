from flask import Flask, render_template_string, request, send_from_directory
from plagiarism_detector import detect_plagiarism_multiple_sources
from highlighter import create_html_report
import os

app = Flask(__name__)

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Plagiarism Detection</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
            color: #102a43;
            padding: 20px;
        }
        h1 {
            color: #334e68;
            text-align: center;
            font-weight: 700;
            margin-bottom: 30px;
        }
        form {
            background: #fff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            max-width: 900px;
            margin: 0 auto 40px auto;
        }
        label {
            font-weight: 600;
            display: block;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        textarea {
            width: 100%;
            border: 2px solid #627d98;
            border-radius: 8px;
            padding: 12px;
            font-size: 1em;
            resize: vertical;
            transition: border-color 0.3s ease;
        }
        textarea:focus {
            border-color: #486581;
            outline: none;
        }
        input[type="submit"] {
            background-color: #486581;
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 1.1em;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            display: block;
            margin: 20px auto 0 auto;
            font-weight: 700;
        }
        input[type="submit"]:hover {
            background-color: #334e68;
        }
        .results {
            max-width: 900px;
            margin: 0 auto;
            background: #fff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        .highlighted-text {
            background-color: #fffae6;
            border-left: 6px solid #f0b429;
            padding: 10px;
            margin-bottom: 20px;
            font-style: italic;
            color: #7b5e00;
        }
        ul {
            list-style-type: none;
            padding-left: 0;
        }
        li {
            background: #d9e2ec;
            margin-bottom: 8px;
            padding: 10px 15px;
            border-radius: 8px;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
            font-weight: 600;
            color: #334e68;
        }
        a.report-link {
            display: inline-block;
            margin-top: 15px;
            padding: 10px 20px;
            background-color: #f0b429;
            color: #334e68;
            font-weight: 700;
            border-radius: 8px;
            text-decoration: none;
            transition: background-color 0.3s ease;
        }
        a.report-link:hover {
            background-color: #d18e00;
            color: white;
        }
        .disclaimer {
            font-size: 0.9em;
            color: #627d98;
            margin-top: 20px;
            text-align: center;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>Plagiarism Detection Tool</h1>
    <form method="post">
        <label for="suspicious_text">Suspicious Text:</label>
        <textarea id="suspicious_text" name="suspicious_text" rows="10" cols="80" required>{{ request.form.suspicious_text or '' }}</textarea>

        <label for="source_texts">Source Texts (separate multiple sources with '---'):</label>
        <textarea id="source_texts" name="source_texts" rows="10" cols="80" required>{{ request.form.source_texts or '' }}</textarea>

        <input type="submit" value="Check Plagiarism">
    </form>

    {% if result %}
    <div class="results">
        <p><strong>Overall Plagiarism Similarity:</strong> {{ similarity }}%</p>

        <h3>Detected Plagiarized Segments:</h3>
        <ul>
        {% for segment in detected_segments %}
            <li>{{ segment.text }} (Chars: {{ segment.suspicious_start_char }}-{{ segment.suspicious_end_char }})</li>
        {% endfor %}
        </ul>

        <h3>Source Matches:</h3>
        <ul>
        {% for source_name, match_info in source_matches.items() %}
            <li>{{ source_name }}: Similarity {{ match_info.similarity }}%, Segments: {{ match_info.segments_count }}</li>
        {% endfor %}
        </ul>

        <a href="/reports/{{ report_file }}" target="_blank" class="report-link">View HTML Report</a>

        <p class="disclaimer">Note: The plagiarism detection results are approximate and may not be fully accurate. Please review carefully.</p>
    </div>
    {% endif %}
</body>
</html>
"""

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    similarity = 0
    detected_segments = []
    source_matches = {}
    report_file = None

    if request.method == 'POST':
        suspicious_text = request.form['suspicious_text']
        source_texts_raw = request.form['source_texts']
        # Split multiple sources by '---' separator
        source_texts_list = [s.strip() for s in source_texts_raw.split('---') if s.strip()]
        source_documents = {f"Source {i+1}": text for i, text in enumerate(source_texts_list)}

        similarity, detected_segments, source_matches = detect_plagiarism_multiple_sources(
            suspicious_text, source_documents, n=4
        )

        # Create HTML report file in reports directory
        report_file_name = "web_report.html"
        report_path = os.path.join(REPORTS_DIR, report_file_name)
        create_html_report(suspicious_text, detected_segments, source_matches, output_file=report_path)

        # Format similarity and match info for display
        similarity = f"{similarity:.2%}"
        for key in source_matches:
            source_matches[key]['similarity'] = f"{source_matches[key]['similarity']:.2%}"

        result = True
        report_file = report_file_name

    return render_template_string(HTML_FORM, result=result, similarity=similarity,
                                  detected_segments=detected_segments, source_matches=source_matches,
                                  report_file=report_file)

@app.route('/reports/<path:filename>')
def serve_report(filename):
    return send_from_directory(REPORTS_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
