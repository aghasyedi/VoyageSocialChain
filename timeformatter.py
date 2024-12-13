from datetime import datetime

def time_ago(post_date_str):
    """
    Converts a post date string to a human-readable time ago format.

    Args:
        post_date_str (str): The post date in the format 'YYYY-MM-DD HH:MM:SS.ssssss'.

    Returns:
        str: A string representing how long ago the post was made.
    """
    try:
        # Convert the string to a datetime object
        post_date = datetime.strptime(post_date_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        return "Invalid date format"

    now = datetime.now()
    diff = now - post_date  # Calculate the time difference

    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)}s ago"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m ago"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days}d ago"
    elif seconds < 2419200:  # 4 weeks
        weeks = int(seconds // 604800)
        return f"{weeks}wk ago"
    elif seconds < 31536000:  # 1 year
        months = int(seconds // 2628000)  # Approx 30.44 days in a month
        return f"{months}mo ago"
    else:
        years = int(seconds // 31536000)
        return f"{years}yr ago"

# Example usage
# print(time_ago('2024-10-03 14:48:15.571314'))
