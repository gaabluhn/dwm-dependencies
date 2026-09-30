# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path
from albert import *

md_iid = "5.0"
md_version = "2.0"
md_name = "Baloo Search"
md_description = "Search files via Baloo (baloosearch6)"
md_license = "MIT"
md_url = ""
md_bin_dependencies = ["baloosearch6"]
md_authors = ["hp"]

MAX_RESULTS = 20
MIN_QUERY_LEN = 3  # avoid firing baloosearch6 on 1-2 char queries while typing

class Plugin(PluginInstance, GlobalQueryHandler):
    def __init__(self):
        PluginInstance.__init__(self)
        GlobalQueryHandler.__init__(self)

    def rankItems(self, context):
        query = context.query.strip()

        if len(query) < MIN_QUERY_LEN:
            return []

        try:
            proc = subprocess.run(
                ["baloosearch6", query],
                capture_output=True, text=True, timeout=5
            )
        except Exception:
            return []

        if not context.isValid:
            return []

        paths = [
            line.strip() for line in proc.stdout.splitlines()
            if line.strip() and not line.startswith("Elapsed:")
        ][:MAX_RESULTS]

        results = []
        for path in paths:
            filename = Path(path).name
            item = StandardItem(
                id=path,
                text=filename,
                subtext=path,
                icon_factory=lambda p=path: Icon.fileType(p),
                actions=[
                    Action("open", "Open", lambda p=path: openFile(p)),
                    Action("copy", "Copy path", lambda p=path: setClipboardText(p)),
                ]
            )
            results.append(RankItem(item, 0.5))
        return results
