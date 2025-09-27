# ai_core.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_match_score(resume_text, jd_text):
    """
    Calculates the similarity score between a resume and a job description
    using TF-IDF and Cosine Similarity.
    Returns a percentage score.
    """
    # Place the texts into a list
    text_documents = [resume_text, jd_text]

    # Create the TF-IDF Vectorizer
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')

    # Convert the text documents into number vectors
    try:
        tfidf_matrix = tfidf_vectorizer.fit_transform(text_documents)
        # Calculate the similarity between the two vectors
        match_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Convert to a percentage
        return match_score * 100
    except ValueError:
        # Happens if one of the documents is empty after removing stop words
        return 0.0