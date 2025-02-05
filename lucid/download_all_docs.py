#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "httpx",
# ]
# ///
import argparse
import os

import httpx

ACCESS_TOKEN = os.getenv("LUCID_TOKEN", False)
FOLDER_ID = os.getenv("LUCID_FOLDER_ID", False)
BASE_URL = "https://api.lucid.co"

headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Lucid-Api-Version": "1"}


def list_folder(folder_id=FOLDER_ID):
    all_results = []
    page_token = None

    with httpx.Client(timeout=60.0) as client:
        while True:
            params = {"pageSize": 200}
            if page_token:
                params["pageToken"] = page_token

            response = client.get(
                f"{BASE_URL}/folders/{folder_id}/contents",
                headers={
                    **headers,
                    "accept": "application/json",
                    "content-type": "application/json",
                },
                params=params,
            )
            response.raise_for_status()

            page_data = response.json()
            if isinstance(page_data, dict):
                page_results = page_data.get("results", [])
                for result in page_results:
                    if result.get("type") == "folder":
                        # Recursively get contents of subfolder
                        subfolder_results = list_folder(result["id"])
                        all_results.extend(subfolder_results["results"])
                    else:
                        # Add documentId as id for compatibility
                        if "documentId" in result:
                            result["id"] = result["documentId"]
                        all_results.append(result)
            else:
                for result in page_data:
                    if result.get("type") == "folder":
                        # Recursively get contents of subfolder
                        subfolder_results = list_folder(result["id"])
                        all_results.extend(subfolder_results["results"])
                    else:
                        # Add documentId as id for compatibility
                        if "documentId" in result:
                            result["id"] = result["documentId"]
                        all_results.append(result)

            # Get next page token from Link header if it exists
            link_header = response.headers.get("Link")
            if not link_header:
                break

            # Extract next page token from Link header
            if "pageToken=" in link_header:
                page_token = link_header.split("pageToken=")[1].split(">")[0]
            else:
                break

        return {"results": all_results}


def download_document(document_id):
    export_dir = f"lucid_export_{FOLDER_ID}"
    os.makedirs(export_dir, exist_ok=True)

    try:
        with httpx.Client(timeout=120.0) as client:
            # First get the document metadata to check pageCount
            meta_response = client.get(
                f"{BASE_URL}/documents/{document_id}",
                headers={**headers, "accept": "application/json"},
            )
            meta_response.raise_for_status()
            metadata = meta_response.json()

            if metadata.get("product") != "lucidchart":
                return None

            if "pageCount" in metadata:
                # Get content for each page
                for page in range(1, metadata["pageCount"] + 1):
                    try:
                        response = client.get(
                            f"{BASE_URL}/documents/{document_id}",
                            headers={
                                **headers,
                                "accept": "image/png",
                            },
                            params={"page": page, "crop": "content"},
                        )
                        response.raise_for_status()
                        safe_title = (
                            metadata["title"]
                            .replace(" ", "_")
                            .replace("/", "_")
                            .replace("\\", "_")
                            .replace(":", "_")
                            .replace("*", "_")
                            .replace("?", "_")
                            .replace('"', "_")
                            .replace("<", "_")
                            .replace(">", "_")
                            .replace("|", "_")
                        )
                        filename = os.path.join(
                            export_dir, f"{safe_title}_page_{page}.png"
                        )
                        with open(filename, "wb") as f:
                            f.write(response.content)
                    except Exception as e:
                        print(
                            f"Failed to download page {page} of document {document_id}: {str(e)}"
                        )
                        continue
                return response.content
            else:
                # No pageCount, get full content
                try:
                    response = client.get(
                        f"{BASE_URL}/documents/{document_id}",
                        headers={
                            **headers,
                            "accept": "image/png",
                        },
                        params={"crop": "content"},
                    )
                    response.raise_for_status()
                    safe_title = (
                        metadata["title"]
                        .replace(" ", "_")
                        .replace("/", "_")
                        .replace("\\", "_")
                        .replace(":", "_")
                        .replace("*", "_")
                        .replace("?", "_")
                        .replace('"', "_")
                        .replace("<", "_")
                        .replace(">", "_")
                        .replace("|", "_")
                    )
                    filename = os.path.join(export_dir, f"{safe_title}.png")
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    return response.content
                except Exception as e:
                    print(f"Failed to download document {document_id}: {str(e)}")
                    return None
    except Exception as e:
        print(f"Failed to get metadata for document {document_id}: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute actual download instead of dry run",
    )
    args = parser.parse_args()

    documents = list_folder()
    for doc in documents.get("results", []):
        doc_id = doc["id"]
        doc_name = doc.get("name", f"document_{doc_id}")
        if args.execute:
            print(f"Downloading document: {doc_name}")
            content = download_document(doc_id)
            if content is not None:
                try:
                    with open(f"{doc_name}.json", "wb") as f:
                        f.write(content)
                except IOError as e:
                    print(f"Failed to write {doc_name}: {str(e)}")
                    continue
            else:
                print(f"Skipping {doc_name} - no content downloaded")
        else:
            print(f"[DRY RUN] Would download document: {doc_name}")


if __name__ == "__main__":
    main()
