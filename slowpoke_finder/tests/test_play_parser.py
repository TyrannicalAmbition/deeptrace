from slowpoke_finder.parsers.playwright import PlaywrightParser


def test_parse_playwright():
    parser = PlaywrightParser()
    steps = parser.parse("examples/playwright_small.json")
    assert len(steps) == 3
    assert steps[0].duration == 4200
