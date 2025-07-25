#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main Module for Plagiarism Detection

This module provides a command-line interface for the plagiarism detector
and includes sample test cases.
"""

import os
import argparse
import sys
from text_processor import preprocess_text
from plagiarism_detector import (
    find_plagiarism_segments,
    detect_plagiarism_multiple_sources
)
from highlighter import create_html_report

def run_test_case():
    """
    Run a sample test case with predefined suspicious and source documents.
    """
    print("Running sample test case...")
    
    suspicious_assignment = """
    The quick brown fox jumps over the lazy dog. This is an example of a sentence that might be plagiarized.
    Natural language processing is a field of artificial intelligence that focuses on the interaction between computers and human language.
    Machine learning algorithms can be trained to recognize patterns in text and identify similarities between documents.
    """

    source_document1 = """
    Natural language processing is a field of artificial intelligence that focuses on the interaction between computers and human language.
    The quick brown fox jumps over the lazy cat. This is an original sentence.
    """
    
    source_document2 = """
    Machine learning algorithms can be trained to recognize patterns in text and identify similarities between documents.
    This is completely original content that should not match anything in the suspicious document.
    """
    
    # Test with a single source document
    print("\n--- Testing with a single source document ---")
    similarity, detected_segments = find_plagiarism_segments(
        suspicious_assignment, source_document1, n=4
    )

    print(f"Overall Plagiarism Similarity: {similarity:.2%}")

    if detected_segments:
        print("\n--- Detected Plagiarized Segments ---")
        for segment in detected_segments:
            print(f"  - Matched Text: '{segment['text']}' (Chars: {segment['suspicious_start_char']}-{segment['suspicious_end_char']})")

        # Create HTML report
        report_file = "single_source_report.html"
        create_html_report(suspicious_assignment, detected_segments, output_file=report_file)
        print(f"\nHTML report created: {report_file}")
    else:
        print("\nNo direct plagiarism detected.")
    
    # Test with multiple source documents
    print("\n--- Testing with multiple source documents ---")
    source_documents = {
        "Source 1": source_document1,
        "Source 2": source_document2
    }
    
    similarity, detected_segments, source_matches = detect_plagiarism_multiple_sources(
        suspicious_assignment, source_documents, n=4
    )
    
    print(f"Overall Plagiarism Similarity: {similarity:.2%}")
    
    if detected_segments:
        print("\n--- Detected Plagiarized Segments ---")
        for segment in detected_segments:
            source = segment.get('source_name', 'unknown')
            print(f"  - Matched Text: '{segment['text']}' (Source: {source})")
        
        # Print source matches
        print("\n--- Source Matches ---")
        for source_name, match_info in source_matches.items():
            print(f"  - {source_name}: Similarity {match_info['similarity']:.2%}, Segments: {match_info['segments_count']}")
        
        # Create HTML report
        report_file = "multi_source_report.html"
        create_html_report(suspicious_assignment, detected_segments, source_matches, output_file=report_file)
        print(f"\nHTML report created: {report_file}")
    else:
        print("\nNo direct plagiarism detected.")

def compare_files(suspicious_file, source_files, n_gram_size=4, output_file=None):
    """
    Compare a suspicious file against one or more source files.
    
    Args:
        suspicious_file (str): Path to suspicious file
        source_files (list): List of paths to source files
        n_gram_size (int): Size of n-grams
        output_file (str): Path to output HTML report
    """
    try:
        # Read suspicious file
        with open(suspicious_file, 'r', encoding='utf-8') as f:
            suspicious_text = f.read()
        
        # Read source files
        source_documents = {}
        for source_file in source_files:
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    source_name = os.path.basename(source_file)
                    source_documents[source_name] = f.read()
            except Exception as e:
                print(f"Error reading source file {source_file}: {str(e)}")
                continue
        
        if not source_documents:
            print("No valid source documents provided.")
            return
        
        # Detect plagiarism
        similarity, detected_segments, source_matches = detect_plagiarism_multiple_sources(
            suspicious_text, source_documents, n=n_gram_size
        )
        
        print(f"Overall Plagiarism Similarity: {similarity:.2%}")
        
        if detected_segments:
            print(f"Found {len(detected_segments)} plagiarized segments.")
            
            # Print source matches
            print("\n--- Source Matches ---")
            for source_name, match_info in source_matches.items():
                print(f"  - {source_name}: Similarity {match_info['similarity']:.2%}, Segments: {match_info['segments_count']}")
            
            # Create HTML report
            if not output_file:
                output_file = f"{os.path.splitext(os.path.basename(suspicious_file))[0]}_plagiarism_report.html"
            
            report_path = create_html_report(suspicious_text, detected_segments, source_matches, output_file=output_file)
            print(f"\nHTML report created: {report_path}")
        else:
            print("\nNo direct plagiarism detected.")
    
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    """
    Main function for command-line interface.
    """
    parser = argparse.ArgumentParser(description='Plagiarism Detection Tool')
    parser.add_argument('--test', action='store_true', help='Run sample test case')
    parser.add_argument('--suspicious', type=str, help='Path to suspicious document')
    parser.add_argument('--sources', type=str, nargs='+', help='Paths to source documents')
    parser.add_argument('--ngram', type=int, default=4, help='N-gram size (default: 4)')
    parser.add_argument('--output', type=str, help='Path to output HTML report')
    
    args = parser.parse_args()
    
    if args.test:
        run_test_case()
    elif args.suspicious and args.sources:
        compare_files(args.suspicious, args.sources, args.ngram, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()