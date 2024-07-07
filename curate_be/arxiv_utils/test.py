from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords(text, top_n=10):
    # Create a TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english', max_features=top_n)
    # Fit and transform the text
    tfidf_matrix = vectorizer.fit_transform([text])
    # Get feature names (words)
    feature_names = vectorizer.get_feature_names_out()
    # Get the tf-idf scores
    tfidf_scores = tfidf_matrix.toarray().flatten()
    # Create a dictionary of words and their tf-idf scores
    keyword_scores = dict(zip(feature_names, tfidf_scores))
    # Sort the keywords based on their scores
    sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_keywords

# Example usage
text = """
Artificial Intelligence (AI) is the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving. The ideal characteristic of artificial intelligence is its ability to rationalize and take actions that have the best chance of achieving a specific goal. 
"""

keywords = extract_keywords(text)
print(keywords)
