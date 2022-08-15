def parse_forms(form, checkboxes: list[str] = []):
    """Parses web form (where input's name = {{object.id}}:property_name;
    If object must be created and so hasn't id, set input's name = NEW:property_name)
    checkboxes are a list of input:[type=checkbox]`s property_names.
    Returns a dict {object.id: dict-represented object}, where dict-represented object
    is a dict {property_name: value}"""
    result = {}
    for key, val in form.lists():
        id_, arg = key.split(":")
        if id_ == "NEW":
            for i, value in enumerate(val):
                id_ = "NEW" + str(i)
                if id_ not in result:
                    result[id_] = dict()
                result[id_][arg] = value
        else:
            val = val[0]
            if id_ not in result:
                result[id_] = dict()

            if val == "on":
                val = True
            result[id_][arg] = val

    for res_dict in result.values():
        for checkbox in checkboxes:
            if checkbox not in res_dict:
                res_dict[checkbox] = False
            else:
                res_dict[checkbox] = True

    return result


def update_objs(session, dicts, class_, not_nullable=None, primary_key_name="id"):
    """Creates or updates databases objects using a dict, parsed from web form"""
    for id_, dict_ in dicts.items():
        if "NEW" not in id_:
            kwargs = {primary_key_name: id_}
            obj = session.query(class_).filter_by(**kwargs).one()
            if "delete" in dict_:
                session.delete(obj)
                continue
            for arg_name, value in dict_.items():
                setattr(obj, arg_name, value)

        else:
            if not_nullable:
                if not dict_[not_nullable]:
                    continue

            obj = class_(**dict_)
            session.add(obj)
    session.commit()
