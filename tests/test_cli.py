"""тесты командной строки"""

from depviz.cli import EXIT_ERROR, EXIT_OK, main


def test_prints_all_parameters(write_config, capsys):
    """печать всех параметров"""
    code = main([write_config()])
    out = capsys.readouterr().out.splitlines()
    assert code == EXIT_OK
    assert out == [
        "package_name: Newtonsoft.Json",
        "repository: https://api.nuget.org/v3/index.json",
        "test_mode: False",
        "output_image: graph.png",
        "ascii_tree: True",
        "filter_substring: ",
    ]


def test_error_goes_to_stderr(capsys):
    """ошибка идёт в stderr"""
    code = main(["no_such_file.yaml"])
    captured = capsys.readouterr()
    assert code == EXIT_ERROR
    assert captured.out == ""
    assert captured.err.startswith("Ошибка:")
