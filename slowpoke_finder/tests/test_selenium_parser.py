from slowpoke_finder.parsers.selenium import SeleniumParser


def test_selenium_parser_examples():
    parser = SeleniumParser()
    result = parser.parse("examples/selenium_array.json")
    assert len(result) == 2
    assert result[0].name == "Click login"
    print("selenium_array.json: OK")

    result = parser.parse("examples/selenium_events.json")
    assert len(result) == 2
    assert result[0].name == "Open page"
    print("selenium_events.json: OK")


def test_selenium_parser_broken():
    parser = SeleniumParser()
    try:
        parser.parse("examples/broken.json")
        assert False, "Exception expected"
    except ValueError:
        print("broken.json: OK")
