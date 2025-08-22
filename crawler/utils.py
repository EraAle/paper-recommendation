import textwrap

def document_print(document: list[dict[str, str]]) -> None:
    """
    Takes a list of paper information and prints it in a human-readable format.

    Args:
        document: The list of documents to print.
    """

    if not document:
        print("document is empty")
        return

    # Print each document with a number
    for i, doc in enumerate(document, 1):
        print(f"\n{'=' * 25} Document {i} {'=' * 25}")

        print(f"Title: {doc.get('title', 'N/A')}")

        print(f"URL: {doc.get('url', 'N/A')}")

        print("Abstract:")

        abstract = doc.get('abstract', 'N/A')
        wrapped_abstract = textwrap.fill(
            abstract,
            width=80,
            initial_indent="    ",
            subsequent_indent="    "
        )
        print(wrapped_abstract)

    print(f"\n{'=' * 58}")