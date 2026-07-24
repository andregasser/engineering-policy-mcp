from __future__ import annotations

import pathspec

from engineering_policy.domain.models import AnalysisConfig


class PathClassifier:
    def __init__(self, config: AnalysisConfig) -> None:
        self._excluded = pathspec.PathSpec.from_lines("gitwildmatch", config.exclude_paths)
        self._tests = pathspec.PathSpec.from_lines("gitwildmatch", config.test_paths)
        self._production = pathspec.PathSpec.from_lines("gitwildmatch", config.production_paths)

    def classify(self, path: str) -> str:
        if self._excluded.match_file(path):
            return "excluded"
        if self._tests.match_file(path):
            return "test"
        if self._production.match_file(path):
            return "production"
        return "other"

    def is_excluded(self, path: str) -> bool:
        return self._excluded.match_file(path)
