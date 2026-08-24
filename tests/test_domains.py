from cdns import compile_domain, compile_domains


class TestCompileDomain:
    def test_matches_an_exact_domain(self):
        pattern = compile_domain('example.com')
        assert pattern.match('example.com') is not None
        assert pattern.match('EXAMPLE.COM') is not None
        assert pattern.match('another.com') is None

    def test_matches_subdomains_with_single_wildcard(self):
        pattern = compile_domain('*.example.com')
        assert pattern.match('cdn.example.com') is not None
        assert pattern.match('static.example.com') is not None
        assert pattern.match('example.com') is None

    def test_does_not_match_double_subdomain_with_single_wildcard(self):
        pattern = compile_domain('*.example.com')
        assert pattern.match('a.b.example.com') is None

    def test_is_case_insensitive(self):
        pattern = compile_domain('Example.Com')
        assert pattern.match('example.com') is not None
        assert pattern.match('EXAMPLE.COM') is not None
        assert pattern.match('eXaMpLe.CoM') is not None

    def test_escapes_dots_in_domain(self):
        pattern = compile_domain('sub.example.com')
        assert pattern.match('subexample.com') is None
        assert pattern.match('subxexample.com') is None
        assert pattern.match('sub.example.com') is not None

    def test_matches_only_the_exact_domain_without_suffix(self):
        pattern = compile_domain('test.org')
        assert pattern.match('test.org') is not None
        assert pattern.match('test.org.evil.com') is None
        assert pattern.match('mytest.org') is None

    def test_matches_wildcard_with_literal_asterisk_strings(self):
        pattern = compile_domain('**.example.com')
        # `**` at start becomes `.*`, so the final pattern is `^.*\.example\.com$`.
        # `.*` can match literal `**`, so "**.example.com" matches as well.
        assert pattern.match('**' + '.example.com') is not None

    def test_matches_wildcard_before_domain_without_leading_dot(self):
        pattern = compile_domain('**example.com')
        assert pattern.match('**example.com') is not None

    def test_handles_single_wildcard_in_middle_of_domain(self):
        pattern = compile_domain('cdn.*.com')
        assert pattern.match('cdn.example.com') is not None
        assert pattern.match('cdn.cdn2.com') is not None  # [^.]+ matches 'cdn2' before the escaped dot

    def test_handles_single_wildcard_at_end_of_domain(self):
        pattern = compile_domain('example.*')
        assert pattern.match('example.com') is not None
        assert pattern.match('example.net') is not None
        assert pattern.match('example.cdn.wow') is None  # [^.]+ only matches one segment


class TestCompileDomains:
    def test_matches_any_of_the_provided_domains(self):
        pattern = compile_domains(['cloudflare.com', 'akamai.net'])
        assert pattern.match('cloudflare.com') is not None
        assert pattern.match('akamai.net') is not None
        assert pattern.match('example.org') is None

    def test_works_with_single_wildcard(self):
        pattern = compile_domains(['*.cdn.example.com'])
        assert pattern.match('a.cdn.example.com') is not None
        assert pattern.match('b.cdn.example.com') is not None
        assert pattern.match('cdn.example.com') is None

    def test_combines_exact_domains_and_wildcards(self):
        pattern = compile_domains(['exact.com', '*.wild.example.com'])
        assert pattern.match('exact.com') is not None
        assert pattern.match('sub.wild.example.com') is not None
        assert pattern.match('other.com') is None

    def test_is_case_insensitive_across_all_domains(self):
        pattern = compile_domains(['Example.com'])
        assert pattern.match('example.com') is not None
        assert pattern.match('EXAMPLE.COM') is not None

    def test_matches_everything_with_empty_array(self):
        pattern = compile_domains([])
        # Empty domains produces re.compile('', re.IGNORECASE) which matches everything
        assert pattern.match('') is not None
        assert pattern.match('anything.com') is not None

    def test_escapes_dots_in_wildcard_domains(self):
        pattern = compile_domain('*.examplecom')
        # Pattern is ^[^.]+\.examplecom$ - dot after wildcard is escaped, cdn.examplecom matches
        assert pattern.match('cdn.examplecom') is not None
        assert pattern.match('cdnexamplecom') is None
