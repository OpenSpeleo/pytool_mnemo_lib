#!/usr/bin/env python

from json import JSONEncoder

from mnemo_lib.sections import Section

class SectionJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Section):
            return obj.asdict()
        return super().default(obj)
