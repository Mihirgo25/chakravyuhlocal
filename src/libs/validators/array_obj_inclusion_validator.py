def array_obj_inclusion_validator(record, attribute, value, options):
    arguments = {}

    for key, value in options.items():
        arguments[key] = value(record) if callable(value) else value

    value_copy = value or []
    if len(list(set(value_copy).difference(set(arguments['inclusion_values'])))) > 0:
        raise Exception(attribute, "can only contain {}".format(', '.join(arguments['inclusion_values']))) 