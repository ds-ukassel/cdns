from cdns import matches, match_headers, header2pattern


class TestMatches:
    def test_returns_true_when_all_headers_match_exactly(self):
        headers = {'content-type': 'text/html'}
        matcher = {'content-type': 'text/html'}
        assert matches(headers, matcher) is True

    def test_returns_true_for_partial_match(self):
        headers = {'content-type': 'text/html', 'x-powered-by': 'Express'}
        matcher = {'content-type': 'text/html'}
        assert matches(headers, matcher) is True

    def test_returns_false_when_a_header_value_differs(self):
        headers = {'content-type': 'text/html'}
        matcher = {'content-type': 'application/json'}
        assert matches(headers, matcher) is False

    def test_handles_null_expected_value_header_must_be_present(self):
        headers = {'content-type': 'text/html'}
        matcher = {'x-custom-header': None}
        assert matches(headers, matcher) is False

    def test_returns_true_when_header_with_null_expected_is_present(self):
        headers = {'x-custom-header': 'exists'}
        matcher = {'x-custom-header': None}
        assert matches(headers, matcher) is True

    def test_handles_lowercase_headers_from_responses(self):
        headers = {'content-type': 'text/html'}
        matcher = {'content-type': 'text/html'}
        assert matches(headers, matcher) is True

    def test_returns_false_when_header_key_mismatch_causes_lookup_to_fail(self):
        headers = {'Content-Type': 'text/html'}
        matcher = {'x-powered-by': 'Express'}
        assert matches(headers, matcher) is False

    def test_returns_true_for_empty_matcher(self):
        headers = {'content-type': 'text/html'}
        matcher = {}
        assert matches(headers, matcher) is True

    def test_handles_multiple_matchers_with_null_values(self):
        headers = {'x-header-a': 'any', 'x-header-b': 'value'}
        matcher = {'x-header-a': None, 'x-header-b': None}
        assert matches(headers, matcher) is True

    def test_returns_false_if_any_header_with_null_expected_is_absent(self):
        headers = {'x-header-a': 'present'}
        matcher = {'x-header-a': None, 'x-header-b': None}
        assert matches(headers, matcher) is False

    def test_handles_missing_header_value_with_non_null_expected(self):
        headers = {}
        matcher = {'content-type': 'text/html'}
        assert matches(headers, matcher) is False

    def test_handles_wildcard(self):
        headers= {'x-header-a': 'value-a'}
        matcher = {'x-header-a': 'value-*'}
        assert matches(headers, matcher) is True

    def test_handles_wildcards(self):
        headers= {'x-header-a': 'value-a-b-c'}
        matcher = {'x-header-a': 'value-*-*-c'}
        assert matches(headers, matcher) is True

    def test_handles_escaped_asterix(self):
        headers= {'x-header-a': 'value-*'}
        matcher = {'x-header-a': 'value-\\*'}
        assert matches(headers, matcher) is True

    def test_handles_escaped_asterix_with_incorrect_header(self):
        headers= {'x-header-a': 'value-a'}
        matcher = {'x-header-a': 'value-\\*'}
        assert matches(headers, matcher) is False

    def test_handles_incorrect_case(self):
        headers= {'x-header-a': 'value-a'}
        matcher = {'x-header-a': 'value-A'}
        assert matches(headers, matcher) is False


class TestMatchHeaders:
    def test_returns_matching_headers_for_a_single_matching_matcher(self):
        headers = {'content-type': 'text/html', 'server': 'nginx'}
        matchers = [{'content-type': 'text/html'}]
        result = match_headers(headers, matchers)
        assert result == {'content-type': 'text/html'}

    def test_returns_empty_dict_when_no_matcher_matches(self):
        headers = {'content-type': 'text/html'}
        matchers = [{'content-type': 'application/json'}]
        result = match_headers(headers, matchers)
        assert result == {}

    def test_collects_keys_from_all_matching_matchers(self):
        headers = {'content-type': 'text/html', 'server': 'nginx', 'x-powered-by': 'Express'}
        matchers = [
            {'content-type': 'text/html'},
            {'server': 'nginx'},
        ]
        result = match_headers(headers, matchers)
        assert result == {
            'content-type': 'text/html',
            'server': 'nginx',
        }

    def test_returns_partial_dict_when_some_matchers_match_and_others_do_not(self):
        headers = {'content-type': 'text/html', 'server': 'apache'}
        matchers = [
            {'content-type': 'text/html'},
            {'server': 'nginx'},
        ]
        result = match_headers(headers, matchers)
        assert result == {'content-type': 'text/html'}

    def test_omits_headers_with_none_values_when_null_expected(self):
        headers = {}
        matchers = [{'x-custom': None}]
        result = match_headers(headers, matchers)
        assert result == {}

    def test_handles_multiple_matchers_with_overlapping_keys(self):
        headers = {'content-type': 'text/html'}
        matchers = [
            {'content-type': 'text/html'},
            {'content-type': 'text/html'},
        ]
        result = match_headers(headers, matchers)
        assert result == {'content-type': 'text/html'}

    def test_is_case_sensitive_for_header_keys(self):
        headers = {'Content-Type': 'text/html'}
        matchers = [{'content-type': 'text/html'}]
        result = match_headers(headers, matchers)
        assert result == {}

    def test_handles_empty_headers_dict(self):
        headers = {}
        matchers = [{'content-type': 'text/html'}]
        result = match_headers(headers, matchers)
        assert result == {}

    def test_handles_empty_matchers_list(self):
        headers = {'content-type': 'text/html'}
        matchers = []
        result = match_headers(headers, matchers)
        assert result == {}

    def test_handles_empty_matcher_dict_within_matchers(self):
        headers = {'content-type': 'text/html'}
        matchers = [{}]
        result = match_headers(headers, matchers)
        assert result == {}

    def test_collects_headers_from_overlapping_keys_across_different_matching_matchers(self):
        headers = {'content-type': 'text/html', 'server': 'nginx'}
        matchers = [
            {'content-type': 'text/html', 'server': 'nginx'},
        ]
        result = match_headers(headers, matchers)
        assert result == {
            'content-type': 'text/html',
            'server': 'nginx',
        }

    def test_returns_headers_with_matched_values_from_response(self):
        headers = {'x-custom': 'value'}
        matchers = [{'x-custom': 'value'}]
        result = match_headers(headers, matchers)
        assert result == {'x-custom': 'value'}

    def test_handles_matcher_with_both_null_and_non_null_expected_values(self):
        headers = {}
        matchers = [{'content-type': 'text/html', 'x-absent': None}]
        result = match_headers(headers, matchers)
        assert result == {}

    def test_matches_when_all_keys_in_matcher_are_present_and_match(self):
        headers = {'a': '1', 'b': '2'}
        matchers = [{'a': '1', 'b': '2'}]
        result = match_headers(headers, matchers)
        assert result == {'a': '1', 'b': '2'}

    def test_does_not_include_extra_headers_beyond_matcher_expectations(self):
        headers = {'content-type': 'text/html', 'server': 'nginx', 'x-extra': 'data'}
        matchers = [{'content-type': 'text/html', 'server': 'nginx'}]
        result = match_headers(headers, matchers)
        assert result == {
            'content-type': 'text/html',
            'server': 'nginx',
        }

    def test_handles_null_value_with_non_matching_key_in_other_matcher(self):
        headers = {}
        matchers = [{'x-absent': None}, {'content-type': 'text/html'}]
        result = match_headers(headers, matchers)
        assert result == {}

    def test_overwrites_value_when_same_key_appears_in_multiple_matching_matchers(self):
        headers = {'content-type': 'text/html'}
        matchers = [
            {'content-type': 'text/html'},
            {'content-type': 'text/html'},
            {'content-type': 'text/html'},
        ]
        result = match_headers(headers, matchers)
        assert result == {'content-type': 'text/html'}

class TestHeaderToPattern:

    def test_value_without_wildcard(self):
        header = "abc"
        expected = "^abc$"
        assert header2pattern(header) == expected

    def test_value_with_wildcard(self):
        header = "a*c"
        expected = "^a.*c$"
        assert header2pattern(header) == expected

    def test_value_with_escaped_asterix(self):
        header = "a\\*c"
        expected = "^a\\*c$"
        assert header2pattern(header) == expected

    def test_value_with_regex_characters(self):
        header = "a.+?^$|c"
        expected = "^a\\.\\+\\?\\^\\$\\|c$"
        assert header2pattern(header) == expected
