import pathlib
import sys
import unittest
from typing import Dict, List
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
try:
    # using tools/ to optimize test run.
    sys.path.append(str(REPO_ROOT))

    from tools.test.heuristics.heuristics_test_mixin import HeuristicsTestMixin
    from tools.testing.target_determination.determinator import (
        AggregatedHeuristics,
        get_test_prioritizations,
        TestPrioritizations,
    )
    from tools.testing.target_determination.heuristics import HEURISTICS
    from tools.testing.target_determination.heuristics.historical_class_failure_correlation import (
        HistoricalClassFailurCorrelation,
    )
    from tools.testing.test_run import TestRun, TestRuns

except ModuleNotFoundError as e:
    print("Can't import required modules, exiting")
    print(e)
    sys.exit(1)

HEURISTIC_CLASS = "tools.testing.target_determination.heuristics.historical_class_failure_correlation."
HEURISTIC_UTILS = "tools.testing.target_determination.heuristics.utils."


def gen_historical_class_failures() -> Dict[str, Dict[str, float]]:
    return {
        "file1": {
            "test1::classA": 0.5,
            "test2::classA": 0.2,
            "test5::classB": 0.1,
        },
        "file2": {
            "test1::classB": 0.3,
            "test3::classA": 0.2,
            "test5::classA": 1.5,
            "test7::classC": 0.1,
        },
        "file3": {
            "test1::classC": 0.4,
            "test4::classA": 0.2,
            "test7::classC": 1.5,
            "test8::classC": 0.1,
        },
    }


ALL_TESTS = [
    "test1",
    "test2",
    "test3",
    "test4",
    "test5",
    "test6",
    "test7",
    "test8",
]


class TestHistoricalClassFailureCorrelation(HeuristicsTestMixin):
    @mock.patch(
        HEURISTIC_CLASS + "_get_historical_test_class_correlations",
        return_value=gen_historical_class_failures(),
    )
    @mock.patch(
        HEURISTIC_UTILS + "query_changed_files",
        return_value=["file1"],
    )
    def test_get_test_priorities(
        self,
        historical_class_failures: Dict[str, Dict[str, float]],
        changed_files: List[str],
    ) -> None:
        tests_to_prioritize = ALL_TESTS

        heuristic = HistoricalClassFailurCorrelation()
        test_prioritizations = heuristic.get_test_priorities(tests_to_prioritize)

        expected = TestPrioritizations(
            tests_being_ranked=tests_to_prioritize,
            probable_relevance=[test for test in historical_class_failures["file1"].keys()]
        )

        print(expected.get_unranked_relevance_tests())

        self.assert_heuristics_match(
            test_prioritizations,
            expected_high_tests=expected.get_high_relevance_tests(),
            expected_probable_tests=expected.get_probable_relevance_tests(),
            expected_unranked_tests=expected.get_unranked_relevance_tests(),
        )



if __name__ == "__main__":
    unittest.main()
