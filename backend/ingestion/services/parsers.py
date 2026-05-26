import csv
import io


def parse_csv(file_obj):
    content = io.StringIO(file_obj.read().decode("utf-8-sig"))
    reader = csv.DictReader(content)
    return [dict(row) for row in reader]
