#!/usr/bin/env python3
"""
Test GraphQL query against a live DataHub instance

This script tests the glossary term usage GraphQL query against your DataHub environment.

Usage:
    python test_graphql_live.py

Author: Jonny Dixon
Date: January 20, 2026
"""

import json
import sys

import requests  # type: ignore[import-untyped]

# Configuration
GMS_SERVER = "https://sok-poc.acryl.io/gms"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhY3RvclR5cGUiOiJVU0VSIiwiYWN0b3JJZCI6Impvbm55LmRpeG9uQGFjcnlsLmlvIiwidHlwZSI6IlBFUlNPTkFMIiwidmVyc2lvbiI6IjIiLCJqdGkiOiJiY2M4MTU3OS01MjA1LTQ0YzAtODNmNS1kNzA4Yzc1OGVlZDEiLCJzdWIiOiJqb25ueS5kaXhvbkBhY3J5bC5pbyIsImV4cCI6MTc3MjEwMDkwMywiaXNzIjoiZGF0YWh1Yi1tZXRhZGF0YS1zZXJ2aWNlIn0.U7AAxIiij1NiPD1FHkI9VjyL96F3mvzvx2ov3Ju4p6A"


def get_glossary_terms():
    """Fetch all glossary terms"""
    query = """
    query searchGlossaryTerms($start: Int!, $count: Int!) {
        search(input: {
            type: GLOSSARY_TERM,
            query: "*",
            start: $start,
            count: $count
        }) {
            total
            searchResults {
                entity {
                    urn
                    ... on GlossaryTerm {
                        properties {
                            name
                        }
                    }
                }
            }
        }
    }
    """

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    all_terms: list[dict[str, str]] = []
    start = 0
    batch_size = 100

    while True:
        variables = {"start": start, "count": batch_size}

        response = requests.post(
            f"{GMS_SERVER}/api/graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        if response.status_code != 200:
            print(f"❌ Failed to fetch glossary terms: {response.status_code}")
            print(response.text)
            return all_terms

        data = response.json()
        if "errors" in data:
            print("❌ GraphQL errors:", json.dumps(data["errors"], indent=2))
            return all_terms

        search_data = data.get("data", {}).get("search", {})
        results = search_data.get("searchResults", [])
        total = search_data.get("total", 0)

        for result in results:
            entity = result.get("entity", {})
            urn = entity.get("urn")
            name = entity.get("properties", {}).get("name")
            if urn and name:
                all_terms.append({"urn": urn, "name": name})

        if len(results) == 0 or start + batch_size >= total:
            break

        start += batch_size

    return all_terms


def test_usage_query(term_urn, term_name):
    """Test the glossary term usage query"""
    query = """
    query getRelatedEntities($termUrn: String!) {
      searchAcrossEntities(
        input: {
          types: [DASHBOARD]
          query: "*"
          start: 0
          count: 10
          filters: [
            {
              field: "glossaryTerms"
              values: [$termUrn]
              condition: EQUAL
            }
          ]
        }
      ) {
        start
        count
        total
        searchResults {
          entity {
            urn
            type
            ... on Dashboard {
              properties {
                name
                description
              }
              platform {
                name
              }
              subTypes {
                typeNames
              }
              container {
                urn
                properties {
                  name
                }
              }
              domain {
                domain {
                  urn
                  properties {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    variables = {"termUrn": term_urn}

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{GMS_SERVER}/api/graphql",
        headers=headers,
        json={"query": query, "variables": variables},
    )

    if response.status_code != 200:
        print(f"❌ Failed to query usage: {response.status_code}")
        print(response.text)
        return None

    data = response.json()
    if "errors" in data:
        print(f"❌ GraphQL errors for term '{term_name}':")
        print(json.dumps(data["errors"], indent=2))
        return None

    return data.get("data", {}).get("searchAcrossEntities", {})


def main():
    print("=" * 80)
    print("Testing Glossary Term Usage GraphQL Query")
    print("=" * 80)
    print(f"\nDataHub Server: {GMS_SERVER}")
    print("\nStep 1: Fetching glossary terms...")
    print("-" * 80)

    terms = get_glossary_terms()

    if not terms:
        print("\n❌ No glossary terms found or unable to fetch them.")
        print("\nTroubleshooting:")
        print("  1. Check if you have glossary terms in DataHub")
        print("  2. Verify the token is valid")
        print("  3. Check network connectivity")
        return 1

    print(f"\n✅ Found {len(terms)} glossary terms")

    if len(terms) <= 10:
        for i, term in enumerate(terms, 1):
            print(f"  {i}. {term['name']}")
    else:
        print(f"\nShowing first 10 of {len(terms)} terms:")
        for i, term in enumerate(terms[:10], 1):
            print(f"  {i}. {term['name']}")
        print(f"  ... and {len(terms) - 10} more")

    print("\nStep 2: Testing usage query for each term...")
    print("-" * 80)

    total_usage = 0
    terms_with_usage = 0

    for term in terms:
        print(f"\n📊 Testing: {term['name']}")
        print(f"   URN: {term['urn']}")

        result = test_usage_query(term["urn"], term["name"])

        if result is None:
            continue

        total = result.get("total", 0)
        results = result.get("searchResults", [])

        if total > 0:
            terms_with_usage += 1
            total_usage += total
            print(f"   ✅ Found {total} dashboard(s) using this term:")

            for i, search_result in enumerate(results[:5], 1):  # Show first 5
                entity = search_result.get("entity", {})
                props = entity.get("properties", {})
                platform = entity.get("platform", {})
                container = entity.get("container", {})
                domain = entity.get("domain", {})

                print(f"\n   {i}. {props.get('name', 'N/A')}")
                print(f"      Type: {entity.get('type', 'N/A')}")
                print(f"      Platform: {platform.get('name', 'N/A')}")

                if container:
                    container_props = container.get("properties", {})
                    print(f"      Container: {container_props.get('name', 'N/A')}")

                if domain:
                    domain_info = domain.get("domain", {})
                    domain_props = domain_info.get("properties", {})
                    print(f"      Domain: {domain_props.get('name', 'N/A')}")

            if total > 5:
                print(f"\n   ... and {total - 5} more")
        else:
            print("   ℹ️  No dashboards using this term")

    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Glossary terms tested: {len(terms)}")
    print(f"Terms with usage: {terms_with_usage}")
    print(f"Total dashboard usage found: {total_usage}")

    if total_usage > 0:
        print("\n✅ SUCCESS! The GraphQL query is working correctly.")
        print("\nNext steps:")
        print("  1. The action will export this data to Snowflake")
        print("  2. You can run the action with: datahub actions -c action.yaml")
        print("  3. Check the usage table in Snowflake after running")
    else:
        print("\nℹ️  No usage data found.")
        print("\nThis could mean:")
        print("  1. Your dashboards don't have glossary terms tagged yet")
        print("  2. You might need to ingest Power BI/Tableau data into DataHub")
        print("  3. Try tagging some dashboards with glossary terms in DataHub UI")

    print("\n" + "=" * 80)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
