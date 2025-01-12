def trigger_all_components(object):
    for component in object.components:
        try:
            component.trigger()
        except AttributeError:
            pass
