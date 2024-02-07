from functools import wraps


def user_endpoint_docstring(first_line, exclude_fields=None):
    """
    Decorator to generate docstring for user endpoint methods.
    This decorator will help to exclude certain fields such as id, email, is_verified from PUT and PATCH endpoints.

    Args:
    - first_line (str): The first line of the docstring.
    - exclude_fields (list or None): List of fields to exclude from the docstring. Default is None.

    Returns:
    - Function: Decorator function.
    """
    if exclude_fields is None:
        exclude_fields = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            return view_func(*args, **kwargs)

        # Generate docstring for the decorated function
        fields_description = """
        - **id (str)**: Universally Unique Identifier (UUID) representing the user's ID.
        - **email (str)**: User's email address.
        - **full_name (str)**: User's full name.
        - **phone_number (str)**: User's phone number.
        - **birthdate (str)**: User's birthdate in "YYYY-MM-DD" format.
        - **address (str)**: User's address.
        - **profile_image (str)**: URL of the user's profile image or null if not set.
        - **preferred_currency (str)**: User's preferred currency.
        - **is_subscribed_to_newsletter (bool)**: Indicates whether the user is subscribed to the newsletter.
        - **is_verified (bool)**: Indicates whether the user's account is verified via email or not.
        """

        if exclude_fields:
            # Remove excluded fields from the docstring
            lines_to_keep = []
            for line in fields_description.splitlines():
                if not any(
                    line.strip().startswith(f"- **{field}") for field in exclude_fields
                ):
                    lines_to_keep.append(line)
            fields_description = "\n".join(lines_to_keep)

        wrapper.__doc__ = f"""
        **{first_line}**

        {fields_description}
        """

        return wrapper

    return decorator
