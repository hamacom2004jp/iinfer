from iinfer.app import common, web, feature
from pathlib import Path
import bottle
import iinfer
import json


class VersionsUsed(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/versions_used')
        def versions_used():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            bottle.response.content_type = 'application/json'
            ret = []
            with open(Path(iinfer.__file__).parent / 'licenses' / 'files.txt', 'r', encoding='utf-8') as f:
                for i, line in enumerate(f.readlines()):
                    parts = line.strip().split('\t')
                    ret.append(parts)
            with open(Path(iinfer.__file__).parent / 'web' / 'assets_license_list.txt', 'r', encoding='utf-8') as f:
                for i, line in enumerate(f.readlines()):
                    parts = line.strip().split('\t')
                    ret.append(parts)
            return json.dumps(ret)
