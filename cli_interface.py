import argparse
from plagiarism_detector import detect_plagiarism_multiple_sources
from highlighter import create_html_report

def main():
    parser = argparse.ArgumentParser(description='Plagiarism Detection CLI')
    parser.add_argument('--suspicious', type=str, required=True, help='Suspicious text to check')
    parser.add_argument('--originals', type=str, nargs='+', required=True, help='Original texts to compare against')
    parser.add_argument('--output', type=str, default='plagiarism_report.html', help='Output HTML report file name')

    args = parser.parse_args()

    suspicious_text = args.suspicious
    original_texts = args.originals

    # Prepare source documents dictionary
    source_documents = {f"Source {i+1}": text for i, text in enumerate(original_texts)}

    similarity, detected_segments, source_matches = detect_plagiarism_multiple_sources(
        suspicious_text, source_documents, n=4
    )

    print(f"Overall Plagiarism Similarity: {similarity:.2%}")

    if detected_segments:
        print(f"Found {len(detected_segments)} plagiarized segments:")
        for segment in detected_segments:
            source = segment.get('source_name', 'unknown')
            print(f" - Matched Text: '{segment['text']}' (Source: {source})")
    else:
        print("No direct plagiarism detected.")

    # Create HTML report
    report_path = create_html_report(suspicious_text, detected_segments, source_matches, output_file=args.output)
    print(f"HTML report created: {report_path}")

if __name__ == "__main__":
    main()
