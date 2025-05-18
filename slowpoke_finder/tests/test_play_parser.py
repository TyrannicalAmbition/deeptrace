from slowpoke_finder.parsers.playwright import PlaywrightParser


def test_playwright_actions() -> None:
    parser = PlaywrightParser()
    steps = parser.parse("examples/playwright_actions.json")
    assert len(steps) == 2
    assert steps[0].name == "click"
    assert steps[1].name == "fill"
    print("playwright_actions.json: OK")


def test_playwright_events() -> None:
    parser = PlaywrightParser()
    steps = parser.parse("examples/playwright_events.json")
    assert len(steps) == 2
    assert steps[0].name == "navigate"
    assert steps[1].name == "click"
    print("playwright_events.json: OK")


def test_playwright_steps() -> None:
    parser = PlaywrightParser()
    steps = parser.parse("examples/playwright_steps.json")
    assert len(steps) == 2
    assert steps[0].name == "hover"
    assert steps[1].name == "click"
    print("playwright_steps.json: OK")


def test_playwright_array() -> None:
    parser = PlaywrightParser()
    steps = parser.parse("examples/playwright_array.json")
    assert len(steps) == 2
    assert steps[0].name == "goto"
    assert steps[1].name == "type"
    print("playwright_array.json: OK")


def test_playwright_no_end() -> None:
    parser = PlaywrightParser()
    steps = parser.parse("examples/playwright_no_end.json")
    assert len(steps) == 2
    assert steps[0].name == "check"
    assert steps[0].end_ms == steps[0].start_ms
    assert steps[1].name == "submit"
    print("playwright_no_end.json: OK")


def test_playwright_broken() -> None:
    parser = PlaywrightParser()
    try:
        parser.parse("examples/broken.json")
        assert False, "Exception expected"
    except ValueError:
        print("broken.json: OK")
