# Re-run this cell
# Preloaded data for validating email domain.
top_level_domains = [
    ".org",
    ".net",
    ".edu",
    ".ac",
    ".gov",
    ".com",
    ".io"
]


def validate_name(name):
    if len(name) > 2:
        return True
    else:
        return False

def validate_email(email):
    if '@' in email:
        return True
    for i in top_level_domains:
        if i in email:
            return True
        else:
            return False

print(validate_email("otito@gmail"))
print(validate_name("otito"))    