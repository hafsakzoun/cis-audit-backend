from elasticsearch import Elasticsearch
import uuid

# Elasticsearch connection
es = Elasticsearch(
    "https://localhost:9200/",
    basic_auth=("elastic", "SV77vJVzH1g9hjkf18cp"),
    verify_certs=False,
)

ES_INDEX = "users"

# Define index mapping (optional but recommended)
index_mapping = {
    "mappings": {
        "properties": {
            "first_name": {"type": "text"},
            "last_name": {"type": "text"},
            "email": {"type": "keyword"},
            "password": {"type": "keyword"}
        }
    }
}

def get_user_by_email(email):
    ensure_index()
    try:
        query = {
            "query": {
                "term": {
                    "email": email.lower()
                }
            }
        }
        result = es.search(index=ES_INDEX, body=query)
        hits = result['hits']['hits']
        if hits:
            return hits[0]['_source']
        return None
    except Exception as e:
        print("Error fetching user by email:", e)
        return None


# Create the index only if it doesn't exist
def ensure_index():
    if not es.indices.exists(index=ES_INDEX):
        try:
            es.indices.create(index=ES_INDEX, body=index_mapping)
            print(f"✅ Index '{ES_INDEX}' created.")
        except Exception as e:
            print(f"❌ Failed to create index '{ES_INDEX}':", e)
    else:
        print(f"ℹ️ Index '{ES_INDEX}' already exists.")

# Save a new user
def save_user(user_data):
    ensure_index()
    try:
        user_data['email'] = user_data['email'].lower()
        user_id = str(uuid.uuid4())
        response = es.index(index=ES_INDEX, id=user_id, document=user_data)
        return response['result'] in ['created', 'updated']
    except Exception as e:
        print("❌ Elasticsearch error while saving user:", e)
        return False
    
# Check if a user already exists by email
def user_exists(email):
    ensure_index()  # Ensure index before searching
    try:
        query = {
            "query": {
                "term": {
                    "email.keyword": email
                }
            }
        }
        result = es.search(index=ES_INDEX, body=query)
        return result['hits']['total']['value'] > 0
    except Exception as e:
        print("❌ Elasticsearch search error:", e)
        return False
