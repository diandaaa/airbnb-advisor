import re
import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Download punkt tokenizer if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


def fetch_amenities_from_db(cursor):
    cursor.execute("SELECT amenity_name FROM Amenities")
    amenities = cursor.fetchall()
    return [item[0] for item in amenities]

def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = text.lower()
    return text

def tokenize_amenities(amenities):
    return [word_tokenize(a) for a in amenities]

def categorize_amenities(cursor):
    amenities = fetch_amenities_from_db(cursor)
    cleaned_amenities = [clean_text(a) for a in amenities]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(cleaned_amenities)

    kmeans = KMeans(n_clusters=10, n_init=10)
    kmeans.fit(X)

    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    cluster_names = get_cluster_names(centroids, vectorizer)
    return list(zip(amenities, labels)), cluster_names

def get_cluster_names(centroids, vectorizer):
    features = vectorizer.get_feature_names_out()
    cluster_names = {}
    for i, centroid in enumerate(centroids):
        most_representative = centroid.argmax()
        cluster_name = features[most_representative]
        cluster_names[i] = cluster_name.capitalize()
    return cluster_names
