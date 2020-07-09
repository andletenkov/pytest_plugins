import string

COMMENT_TEMPLATE = string.Template("$nodeid: {color:$color}*$is_passed*{color}")


def get_mark_list(item, name):
    return [mark.args[0] for mark in filter(lambda x: x.name == name, item.own_markers) if mark and mark.args]


def get_test_parameters(item):
    params = {}
    parametrize_marks = get_mark_list(item, "parametrize")

    if not parametrize_marks:
        return params

    param_keys = []
    for m in parametrize_marks:
        param_keys.extend([k.strip() for k in m.split(",")])

    params = {k: item.callspec.getparam(k) for k in param_keys}

    return params


def get_allure_title(item, params):
    result = item.nodeid

    if not hasattr(item, "issue") or not item.issue:
        return result

    tflo_key = item.issue.key
    tflo_summary = item.issue.fields.summary

    result = f"{tflo_key}. {tflo_summary}."

    if params:
        param_info = ", ".join([f"'{p}': {{{p}}}" for p in params.keys()])
        result += f" Параметры: {param_info}"

    return result


def get_pretty_name(item, params):
    return get_allure_title(item, params).format(**params)
