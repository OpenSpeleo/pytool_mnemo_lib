#!/usr/bin/env python

from datetime import datetime
from json import JSONEncoder


class SectionJSONEncoder(JSONEncoder):
    def default(self, obj):

        from mnemo_lib.sections import Section
        if isinstance(obj, Section):
            return obj.asdict()

        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M")

        return super().default(obj)
