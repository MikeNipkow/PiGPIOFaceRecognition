import datetime
import os.path


def log(message):
    # Null check.
    if message is None:
        return

    # Get date and time string.
    current_date_time = datetime.datetime.now()
    date = "%s.%s.%s" % (current_date_time.day, current_date_time.month, current_date_time.year)
    time = "%s:%s:%s" % (current_date_time.hour, current_date_time.minute, current_date_time.second)
    current_date_time_string = "[" + date + " " + time + "]"

    # Print the message.
    print(current_date_time_string + " " + message)


# Converts a string to a normalized path.
def convert_string_to_path(raw_string):
    return os.path.normpath(raw_string)
