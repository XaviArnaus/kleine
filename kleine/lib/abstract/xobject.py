from __future__ import annotations

class xObject(object):

    def __init__(self, dict_obj: dict = None):
        if dict_obj:
            self.__dict__.update(
                map(lambda kv: (kv[0].replace(' ', '_'), kv[1]), dict_obj.items()))

    @staticmethod
    def from_dict(dict_obj: dict) -> xObject:
        return xObject(dict_obj=dict_obj)

