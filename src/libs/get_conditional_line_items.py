def conditional_line_items(rate, local_rate):
    new_line_items = []
    for item in local_rate['data']['line_items']:
        if item.get('conditions'):
            operator = item['conditions'].get('operator')
            values = item['conditions'].get('values')
            if operator == "or":
                condition_met = False
                for val in values:
                    key = val[0]
                    operator = val[1]
                    operand = val[2]
                    if isinstance(operand, list):
                        if operator == "IN" or "in":
                            if rate.get(key) in operand:
                                condition_met = True
                            else:
                                condition_met = False
                                break
                    else:
                        if eval("'{}' {} '{}'".format(rate.get(key),operator,operand)):
                            condition_met = True
                            break
                if condition_met:
                    new_line_items.append(item)
            elif operator == "and":
                condition_met = True
                for val in values:
                    key = val[0]
                    operator = val[1]
                    operand = val[2]
                    if isinstance(operand, list):
                        if operator == "IN" or "in":
                            if rate.get(key) in operand:
                                condition_met = True
                            else:
                                condition_met = False
                                break
                    else:
                        if not eval("'{}' {} '{}'".format(rate.get(val[0]),val[1],val[2])):
                            condition_met = False
                            break
                if condition_met:
                    new_line_items.append(item)
        else:
            new_line_items.append(item)
    local_rate['data']['line_items'] = new_line_items
    local_rate['line_items'] = new_line_items

    return local_rate