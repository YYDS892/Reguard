from packaging.specifiers import Specifier


def test_exclusive_prerelease_upper_bound_matches_earlier_prerelease():
    # Explicit prerelease upper bound must enable matching an earlier prerelease.
    assert Specifier("<3.0.0a8").contains("3.0.0a7")


def test_exclusive_prerelease_lower_bound_matches_later_prerelease():
    # Explicit prerelease lower bound must enable matching a later prerelease.
    assert Specifier(">3.0.0a7").contains("3.0.0a8")


def test_final_release_boundary_keeps_prerelease_exclusion():
    # A final-release boundary must keep the default prerelease exclusion.
    assert not Specifier("<3.0.0").contains("3.0.0a7")
