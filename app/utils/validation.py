def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    # Add more rules
    return True, ""