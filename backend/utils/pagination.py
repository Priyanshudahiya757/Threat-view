"""Small helper for consistently shaping paginated API responses."""


def serialize_pagination(pagination, schema) -> dict:
    """Turn a Flask-SQLAlchemy `Pagination` object into the standard
    envelope every list endpoint in this API returns:

        {items, page, per_page, total_items, total_pages}
    """
    return {
        "items": schema.dump(pagination.items, many=True),
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_items": pagination.total,
        "total_pages": pagination.pages,
    }
