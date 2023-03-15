from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

def service_object_validator(record, attribute, value, options):
    value_dup = value
    if not value:
        raise Exception(attribute, "can't be blank")

    if type(value) != "<class 'list'>":
      value = [value]

    filters = {'id': value } | (options['filters'])

    extra_params = options['extra_params']

    params = extra_params | {'filters': filters, 'pagination_data_required': False, 'page_limit': MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT}

    objects = eval("client.ruby.list_{}({})}".format(options['object'],params))['list']

    if objects.count != value.count:
      raise Exception(attribute, "can't be blank")

    if options['store_in']:
        if type(value_dup) == "<class 'list'>":
            options['store_in'] = objects
        else:
            options['store_in']  = objects[0]
    
    if options['callbacks']:
        for callback in options['callbacks']:
            eval(callback(options['store_in']))

    return True