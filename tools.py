from googlesearch import search

def google_search(query: str) -> str:
    """
    Performs a Google search and returns the top 5 results.

    Args:
        query: The search query.

    Returns:
        A string containing the search results.
    """
    try:
        search_results = search(query, num_results=5)
        return "\n".join(search_results)
    except Exception as e:
        return f"Error performing search: {e}"