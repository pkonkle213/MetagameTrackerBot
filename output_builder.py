from typing import Any

from services.command_error_service import KnownError


def MaxLength(headers: list[str], collection: list[Any]):
    """Determines the width of each column based upon the headers and data in that column"""
    buffer = 2
    maxLengths: list[int] = []
    for header in headers:
        maxLengths.append(len(header) + buffer)

    for item in collection:
        for i in range(len(headers)):
            length = len(str(item[i])) + buffer
            maxLengths[i] = max(maxLengths[i], length)

    maxLengths[len(maxLengths) - 1] -= 2
    return maxLengths


def BuildTableOutput(title: str, headers: list[str], items: list[Any]) -> list[str]:
    """Builds a table output out of the title, headers, and items provided"""
    list_output: list[str] = []
    if len(headers) == 0 or len(title) == 0 or len(items) == 0:
        raise KnownError("Insufficient information provided")
    column_widths = MaxLength(headers, items)
    align = ""
    output = f"```{title}\n\n"

    for header in headers:
        width = "{:" + align + str(column_widths[headers.index(header)]) + "s}"
        output += width.format(header)

    pre_elements = output + "\n" + "-" * sum(column_widths) + "\n"
    post_elements = ""

    for item in items:
        line = ""
        for i in range(len(column_widths)):
            element = str(item[i])
            column_format = "{:" + align + str(column_widths[i]) + "s}"
            if element[0] == "-":
                line = line[:-1]

            line += column_format.format(element)

        if len(pre_elements) + len(post_elements) + len(line) > 1997:
            list_output.append(pre_elements + post_elements + "```")
            post_elements = ""

        post_elements += line + "\n"

    list_output.append(pre_elements + post_elements + "```")
    return list_output
