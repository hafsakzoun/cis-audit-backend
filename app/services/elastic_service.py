import csv
import io
import json
from elasticsearch import Elasticsearch, helpers

# Initialize Elasticsearch client
es = Elasticsearch(
    "https://localhost:9200/",
    basic_auth=("elastic", "SV77vJVzH1g9hjkf18cp"),
    verify_certs=False,
)

INDEX_NAME = "cis_controls"

def csv_to_ndjson(file_stream):
    """
    Converts uploaded CSV file stream to NDJSON format (in memory).
    Returns a list of bulk actions for Elasticsearch helpers.bulk().
    """
    try:
        decoded = file_stream.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded))

        actions = []
        for row in reader:
            actions.append({
                "_index": INDEX_NAME,
                "_source": row
            })

        return actions
    except Exception as e:
        raise RuntimeError(f"Failed to convert CSV to NDJSON: {str(e)}")

def index_ndjson_to_es(actions):
    """
    Uses Elasticsearch's bulk helper to index actions.
    """
    try:
        success, errors = helpers.bulk(es, actions)
        if errors:
            return {
                "status": "error",
                "message": "Some documents failed to index.",
                "details": errors
            }
        return {"status": "success", "message": f"{success} documents indexed successfully."}
    except Exception as e:
        return {
            "status": "error",
            "message": f"Exception occurred while indexing: {str(e)}"
        }

def get_all_categories():
    query = {
        "size": 10000,
        "_source": ["Category"],
        "query": {"match_all": {}}
    }
    result = es.search(index="cis_controls", body=query)
    categories = list({
        hit["_source"].get("Category")
        for hit in result["hits"]["hits"]
        if "Category" in hit["_source"]
    })
    return categories

def get_solutions_by_category(category):
    query = {
        "size": 10000,
        "_source": ["Editor Name"],
        "query": {"match": {"Category": category}}
    }
    result = es.search(index="cis_controls", body=query)
    solutions = list({
        hit["_source"].get("Editor Name")
        for hit in result["hits"]["hits"]
        if "Editor Name" in hit["_source"]
    })
    return solutions

def get_solution_versions(category, solution):
    query = {
        "size": 10000,
        "_source": ["Version"],
        "query": {
            "bool": {
                "must": [
                    {"match": {"Category": category}},
                    {"match": {"Editor Name": solution}}
                ]
            }
        }
    }
    result = es.search(index="cis_controls", body=query)
    versions = list({
        hit["_source"].get("Version")
        for hit in result["hits"]["hits"]
        if "Version" in hit["_source"]
    })
    return versions

def get_benchmark_versions(category, solution):
    query = {
        "size": 10000,
        "_source": ["Benchmark Version"],
        "query": {
            "bool": {
                "must": [
                    {"match": {"Category": category}},
                    {"match": {"Editor Name": solution}}
                ]
            }
        }
    }
    result = es.search(index="cis_controls", body=query)
    benchmark_versions = list({
        hit["_source"].get("Benchmark Version")
        for hit in result["hits"]["hits"]
        if "Benchmark Version" in hit["_source"]
    })
    return benchmark_versions

def search_controls(category, version, benchmark_version, editor_name):
    must_clauses = []
    if category and category != "*":
        must_clauses.append({"match": {"Category": category}})
    if version and version != "*":
        must_clauses.append({"term": {"Version": version}})
    if benchmark_version and benchmark_version != "*":
        must_clauses.append({"term": {"Benchmark Version": benchmark_version}})
    if editor_name and editor_name != "*":
        must_clauses.append({"term": {"Editor Name": editor_name}})

    query = {"bool": {"must": must_clauses}}

    results = es.search(index="cis_controls", query=query, size=100)
    return results["hits"]["hits"]
