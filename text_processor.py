#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Text Processor Module for Plagiarism Detection

This module provides functions for text preprocessing, n-gram generation,
and similarity calculation.
"""

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams

# Download NLTK data (uncomment these lines for first-time use)
# nltk.download('punkt')
# nltk.download('stopwords')

def preprocess_text(text):
    """
    Preprocess text by converting to lowercase, removing punctuation,
    tokenizing, and removing stopwords.

    Args:
        text (str): Raw text string

    Returns:
        list: List of filtered tokens
    """
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return filtered_tokens

def preprocess_text_with_offsets(text):
    """
    Preprocess text while preserving character offsets for highlighting.

    Args:
        text (str): Raw text string

    Returns:
        list: List of tuples (token, start_char, end_char)
    """
    clean_text = text.lower()
    # Replace punctuation with spaces to avoid merging words
    clean_text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', clean_text)

    tokens_with_offsets = []
    words = re.finditer(r'\b\w+\b', clean_text)  # Find word boundaries

    stop_words = set(stopwords.words('english'))

    for match in words:
        word = match.group(0)
        start_char = match.start()
        end_char = match.end()

        # Filter stop words here if desired, but keep original offsets for highlighting
        if word not in stop_words:
            tokens_with_offsets.append((word, start_char, end_char))

    return tokens_with_offsets

def generate_ngrams(tokens, n=3):
    """
    Generate n-grams from a list of tokens.

    Args:
        tokens (list): List of tokens
        n (int): Size of n-grams

    Returns:
        list: List of n-grams
    """
    return list(ngrams(tokens, n))

def calculate_similarity(suspicious_tokens, source_tokens, n=3):
    """
    Calculate similarity score between two texts using n-gram overlap.

    Args:
        suspicious_tokens (list): Tokens from suspicious document
        source_tokens (list): Tokens from source document
        n (int): Size of n-grams

    Returns:
        float: Similarity score (0-1)
    """
    suspicious_ngrams = set(generate_ngrams(suspicious_tokens, n))
    source_ngrams = set(generate_ngrams(source_tokens, n))

    if not suspicious_ngrams:
        return 0.0  # Avoid division by zero

    common_ngrams = suspicious_ngrams.intersection(source_ngrams)
    similarity_score = len(common_ngrams) / len(suspicious_ngrams)

    return similarity_score
