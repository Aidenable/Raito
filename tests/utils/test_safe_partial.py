from raito.utils.helpers.safe_partial import safe_partial


def target(a, b, c=3):
    return (a, b, c)


def test_keeps_only_matching_kwargs():
    bound = safe_partial(target, b=2, c=9, unexpected="drop")
    assert bound(1) == (1, 2, 9)


def test_ignores_all_unknown_kwargs():
    bound = safe_partial(target, foo="x", bar="y")
    assert bound(1, 2) == (1, 2, 3)


def test_no_kwargs_behaves_like_original():
    bound = safe_partial(target)
    assert bound(1, 2, 4) == (1, 2, 4)


def test_unknown_kwarg_is_not_forwarded():
    def only_a(a):
        return a

    bound = safe_partial(only_a, a=5, b=6)
    assert bound() == 5


def test_keyword_only_parameters_are_accepted():
    def kw_only(a, *, flag=False):
        return (a, flag)

    bound = safe_partial(kw_only, flag=True, junk="nope")
    assert bound(1) == (1, True)


def test_var_keyword_params_are_not_captured():
    # **kwargs is VAR_KEYWORD, not POSITIONAL_OR_KEYWORD/KEYWORD_ONLY,
    # so arbitrary names are filtered out.
    def with_var_kwargs(a, **kwargs):
        return (a, kwargs)

    bound = safe_partial(with_var_kwargs, anything="x")
    assert bound(1) == (1, {})


def test_wraps_preserves_metadata():
    bound = safe_partial(target, b=2)
    assert bound.__name__ == "target"


def test_bound_kwarg_is_overridden_by_call_time_value():
    bound = safe_partial(target, c=100)
    assert bound(1, 2) == (1, 2, 100)
    # call-time keyword takes precedence over the pre-bound one
    assert bound(1, 2, c=5) == (1, 2, 5)
