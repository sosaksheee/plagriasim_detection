"""
Highlighter module to create HTML reports highlighting plagiarized segments.
"""

def create_html_report(suspicious_text, detected_segments, source_matches=None, output_file="plagiarism_report.html"):
    """
    Create an HTML report highlighting plagiarized segments in the suspicious text.

    Args:
        suspicious_text (str): The suspicious document text.
        detected_segments (list): List of detected plagiarized segments with start and end character indices.
        source_matches (dict, optional): Dictionary of source matches with similarity info.
        output_file (str): Path to output HTML file.

    Returns:
        str: Path to the created HTML report.
    """
    # Basic HTML template with inline CSS for highlighting
    html_content = """
    <html>
    <head>
        <title>Plagiarism Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .highlight { background-color: yellow; }
            .segment { margin-bottom: 10px; padding: 5px; border: 1px solid #ccc; }
            .source-info { font-size: 0.9em; color: #555; }
        </style>
    </head>
    <body>
        <h1>Plagiarism Detection Report</h1>
    """

    # Highlight plagiarized segments in the suspicious text
    last_index = 0
    highlighted_text = ""
    for segment in sorted(detected_segments, key=lambda s: s['suspicious_start_char']):
        start = segment['suspicious_start_char']
        end = segment['suspicious_end_char']
        # Append text before the segment
        highlighted_text += suspicious_text[last_index:start]
        # Append highlighted segment
        highlighted_text += f"<span class='highlight'>{suspicious_text[start:end]}</span>"
        last_index = end
    # Append remaining text
    highlighted_text += suspicious_text[last_index:]

    html_content += f"<p>{highlighted_text}</p>"

    # Add source matches summary if available
    if source_matches:
        html_content += "<h2>Source Matches</h2><ul>"
        for source_name, match_info in source_matches.items():
            similarity = match_info.get('similarity', 0)
            segments_count = match_info.get('segments_count', 0)
            html_content += f"<li>{source_name}: Similarity {similarity:.2%}, Segments {segments_count}</li>"
        html_content += "</ul>"

    html_content += """
    </body>
    </html>
    """

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_file
