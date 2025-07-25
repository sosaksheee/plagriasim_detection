#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams

def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return filtered_tokens

def preprocess_text_with_offsets(text):
    clean_text = text.lower()
    clean_text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', clean_text)
    tokens_with_offsets = []
    words = re.finditer(r'\\b\\w+\\b', clean_text)
    stop_words = set(stopwords.words('english'))
    for match in words:
        word = match.group(0)
        start_char = match.start()
        end_char = match.end()
        if word not in stop_words:
            tokens_with_offsets.append((word, start_char, end_char))
    return tokens_with_offsets

def generate_ngrams(tokens, n=3):
    return list(ngrams(tokens, n))

def calculate_similarity(suspicious_tokens, source_tokens, n=3):
    suspicious_ngrams = set(generate_ngrams(suspicious_tokens, n))
    source_ngrams = set(generate_ngrams(source_tokens, n))
    if not suspicious_ngrams:
        return 0.0
    common_ngrams = suspicious_ngrams.intersection(source_ngrams)
    similarity_score = len(common_ngrams) / len(suspicious_ngrams)
    return similarity_score
