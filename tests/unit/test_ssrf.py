from popular_rules_icon.ssrf import SSRFError, assert_safe_url

def test_rejects_http():
    try:
        assert_safe_url("http://example.com/x")
        assert False
    except SSRFError as e:
        assert e.code == "SSRF_BLOCKED"

def test_rejects_localhost():
    try:
        assert_safe_url("https://localhost/x")
        assert False
    except SSRFError:
        pass
