"""Experimental text classification. No student-score prediction."""
from functools import lru_cache
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from .seed import make_questions

@lru_cache(maxsize=1)
def classifier():
    data = make_questions()
    model = make_pipeline(TfidfVectorizer(analyzer='char', ngram_range=(2,5), sublinear_tf=True), LinearSVC(random_state=42))
    model.fit([q['prompt'] for q in data], [q['topic'] for q in data])
    return model

def predict_topic(prompt):
    return str(classifier().predict([prompt])[0])
