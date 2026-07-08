"""
HTTP Header Grabber Module
Fetches response headers and status for a given URL.
"""

import argparse

import requests


def get_headers(url, timeout=5):
    """
    Fetch headers for a URL.

    Returns a dict:
    {
        "url": str,
        "status_code": int or None,
        "headers": dict,
        "error": str or None
    }
    """
    result = {"url": url, "status_code": None, "headers": {}, "error": None}

    try:
        response = requests.get(url, timeout=timeout)
        result["status_code"] = response.status_code
        result["headers"] = dict(response.headers)
    except requests.exceptions.RequestException as e:
        result["error"] = str(e)

    return result


def print_report(result):
    if result["error"]:
        print(f"Error: {result['error']}")
        return
    print(f"\nStatus Code: {result['status_code']}")
    print("\nHeaders:")
    for key, value in result["headers"].items():
        print(f"{key}: {value}")


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Fetch HTTP response headers for a URL.")
    parser.add_argument("url", help="Target URL, e.g. https://example.com")
    parser.add_argument("--timeout", type=float, default=5, help="Request timeout in seconds (default: 5)")
    return parser


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    result = get_headers(args.url, timeout=args.timeout)
    print_report(result)
