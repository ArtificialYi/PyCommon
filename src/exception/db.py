class UnsupportedSqlTypesError(Exception):  # pragma: no cover
    """Raised when a database type is not supported by the application."""
    pass


class MultipleResultsFound(Exception):  # pragma: no cover
    """Raised when multiple database rows were found for a query that
    expected only one.
    """
    pass
