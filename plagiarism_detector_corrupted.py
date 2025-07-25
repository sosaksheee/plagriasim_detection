#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plagiarism Detector Module

This module provides functions for detecting plagiarism by comparing
suspicious documents against source documents.
"""

from text_processor import (
    preprocess_text,
    preprocess_text_with_offsets,
    generate_ngrams,
    calculate_similarity
)

def find_matching_ngrams(suspicious_tokens, source_tokens, n=3):
    """
    Find matching n-grams between suspicious and source documents.
    
    Args:
        suspicious_tokens (list): Tokens from suspicious document
        source_tokens (list): Tokens from source document
        n (int): Size of n-grams
        
    Returns:
        list: List of dictionaries containing match information
    """
    suspicious_ngrams = generate_ngrams(suspicious_tokens, n)
    source_ngrams = generate_ngrams(source_tokens, n)

    matches = []  # Stores match information
    
    # Convert source ngrams to a set for faster lookup
    source_ngrams_set = set(source_ngrams)

    for i, s_ngram in enumerate(suspicious_ngrams):
        if s_ngram in source_ngrams_set:
            # For direct plagiarism, a match means 100% similarity for that n-gram
            # Find where this ngram starts in the suspicious document (token index)
            s_start_token_idx = i
            s_end_token_idx = i + n - 1

            # Join the tokens to reconstruct the segment for the suspicious document
            matched_suspicious_segment = " ".join(suspicious_tokens[s_start_token_idx:s_end_token_idx + 1])
            
            matches.append({
                'suspicious_text': matched_suspicious_segment,
                'suspicious_start_token': s_start_token_idx,
                'suspicious_end_token': s_end_token_idx,
                'similarity': 1.0  # Direct match
            })
    
    return matches

def find_plagiarism_segments(suspicious_raw_text, source_raw_text, n=4, similarity_threshold=0.8):
    """
    Find plagiarized segments between suspicious and source documents.
    
    Args:
        suspicious_raw_text (str): Raw text from suspicious document
        source_raw_text (str): Raw text from source document
        n (int): Size of n-grams
        similarity_threshold (float): Threshold for considering a segment as plagiarized
        
    Returns:
        tuple: (overall_similarity, plagiarized_segments)
    """
    # Process text with character offsets for highlighting
    suspicious_tokens_info = preprocess_text_with_offsets(suspicious_raw_text)
    source_tokens_info = preprocess_text_with_offsets(source_raw_text)

    # Extract just the tokens for n-gram generation
    suspicious_words = [token[0] for token in suspicious_tokens_info]
    source_words = [token[0] for token in source_tokens_info]

    # Generate n-grams
    suspicious_ngrams_raw = list(generate_ngrams(suspicious_words, n))
    source_ngrams_raw = list(generate_ngrams(source_words, n))

    # Create a dictionary for quick lookup of source n-grams and their original token indices
    source_ngram_map = {}
    for i, s_ngram in enumerate(source_ngrams_raw):
        source_ngram_map.setdefault(s_ngram, []).append(i)

    plagiarized_segments = []  # List of dictionaries with segment information

    for i, s_ngram in enumerate(suspicious_ngrams_raw):
        if s_ngram in source_ngram_map:
            # Found a direct n-gram match
            # Get the character offsets for this n-gram in the suspicious text
            s_start_token_idx = i
            s_end_token_idx = i + n - 1
            
            # Get the actual character offsets from the token info
            start_char_suspicious = suspicious_tokens_info[s_start_token_idx][1]
            end_char_suspicious = suspicious_tokens_info[s_end_token_idx][2]
            
            # Reconstruct the matched text for reporting
            matched_text = suspicious_raw_text[start_char_suspicious:end_char_suspicious]

            # For the source document, find the matching segment's character offsets
            source_start_idx = source_ngram_map[s_ngram][0]
            source_end_idx = source_start_idx + n - 1
            
            start_char_source = source_tokens_info[source_start_idx][1]
            end_char_source = source_tokens_info[source_end_idx][2]
            
            plagiarized_segments.append({
                'text': matched_text,
                'suspicious_start_char': start_char_suspicious,
                'suspicious_end_char': end_char_suspicious,
                'source_start_char': start_char_source,
                'source_end_char': end_char_source
            })
    
    # Calculate overall similarity score (percentage of shared n-grams)
    overall_similarity = calculate_similarity(suspicious_words, source_words, n)

    return overall_similarity, plagiarized_segments

def detect_plagiarism_multiple_sources(suspicious_raw_text, source_documents, n=4, similarity_threshold=0.8):
    """
    Detect plagiarism by comparing a suspicious document against multiple source documents.
    
    Args:
        suspicious_raw_text (str): Raw text from suspicious document
        source_documents (dict): Dictionary of {source_name: source_text}
        n (int): Size of n-grams
        similarity_threshold (float): Threshold for considering a segment as plagiarized
        
    Returns:
        tuple: (overall_similarity, plagiarized_segments, source_matches)
    """
    all_plagiarized_segments = []
    source_matches = {}
    max_similarity = 0.0
    
    for source_name, source_text in source_documents.items():
        similarity, segments = find_plagiarism_segments(
            suspicious_raw_text, source_text, n, similarity_threshold
        )
        
        if segments:
            # Add source information to each segment
            for segment in segments:
                segment['source_name'] = source_name
            
            all_plagiarized_segments.extend(segments)
            source_matches[source_name] = {
                'similarity': similarity,
                'segments_count': len(segments)
            }
            
            # Track the highest similarity score
            if similarity > max_similarity:
                max_similarity = similarity
    
    # Sort segments by start position for easier processing
    all_plagiarized_segments.sort(key=lambda x: x['suspicious_start_char'])
    
    # Merge overlapping segments
    merged_segments = merge_overlapping_segments(all_plagiarized_segments)
    
    return max_similarity, merged_segments, source_matches

def merge_overlapping_segments(segments):
    """
    Merge overlapping plagiarized segments to avoid redundant highlighting.
    
    Args:
        segments (list): List of plagiarized segments
        
    Returns:
        list: List of merged segments
    """
    if not segments:
        return []
    
    # Sort segments by start position
    sorted_segments = sorted(segments, key=lambda x: x['suspicious_start_char'])
    
    merged = [sorted_segments[0]]
    
    for current in sorted_segments[1:]:
        previous = merged[-1]
        
        # Check if segments overlap
        if current['suspicious_start_char'] <= previous['suspicious_end_char']:
            # Merge the segments
            previous['suspicious_end_char'] = max(previous['suspicious_end_char'], 
                                                current['suspicious_end_char'])
            # Update the text to reflect the merged segment
            previous['text'] = previous['text'] + current['text'][
                previous['suspicious_end_char'] - current['suspicious_start_char']:]
            
            # If the segments are from different sources, keep track of all sources
            if 'source_name' in current and 'source_name' in previous:
                if current['source_name'] != previous['source_name']:
                    if 'sources' not in previous:
                        previous['sources'] = [previous['source_name']]
                    if current['source_name'] not in previous['sources']:
                        previous['sources'].append(current['source_name'])
        else:
            merged.append(current)
    
    return merged