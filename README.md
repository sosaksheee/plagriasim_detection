# plagriasim_detection
detects direct plagriasm

We'll focus on identifying exact or near-exact matches of text segments between an "assignment" document and a "source" document (or a collection of source documents).

#Key Concepts & Techniques We'll Use:

1.Text Preprocessing: Cleaning and normalizing text.

2.N-grams: Sequences of N words. Comparing N-grams is excellent for direct plagiarism.

3.Hashing (Optional but good for efficiency): Using techniques like Rolling Hashes (e.g., Rabin-Karp or Winnowing) to quickly find identical or near-identical sequences of N-grams. This is more efficient than direct string comparison for large texts.

4.Similarity Metric: Jaccard Similarity (for N-grams) or Cosine Similarity (if using TF-IDF for smaller chunks). For direct plagiarism, a simple overlap of n-grams or string matching can be very effective.

5.Highlighting Logic: Once similar segments are identified, we'll need a way to mark them in the original text.
