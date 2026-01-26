"""Tests for CLI main module."""

import pytest

from metaeval.cli.main import create_parser, app


class TestCreateParser:
    """Tests for argument parser creation."""

    def test_parser_created(self):
        """Test parser is created successfully."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "metaeval"

    def test_version_argument(self):
        """Test version argument exists."""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        assert exc_info.value.code == 0

    def test_verbose_argument(self):
        """Test verbose argument."""
        parser = create_parser()
        args = parser.parse_args(["-v", "prompts"])
        assert args.verbose is True

    def test_subcommands_exist(self):
        """Test that expected subcommands exist."""
        parser = create_parser()
        # Only test subcommands that don't require positional args
        subcommands_no_args = ["prompts", "config"]

        for cmd in subcommands_no_args:
            # This should not raise
            args = parser.parse_args([cmd])
            assert args.command == cmd

        # Test that other subcommands are registered (by checking help doesn't fail)
        subcommands_with_args = ["download", "convert", "variants", "analyze", "judge", "report"]
        for cmd in subcommands_with_args:
            # Just verify the subcommand is recognized by checking parser doesn't raise on help
            try:
                parser.parse_args([cmd, "--help"])
            except SystemExit as e:
                # --help causes SystemExit(0) which is expected
                assert e.code == 0


class TestDownloadCommand:
    """Tests for download command parsing."""

    def test_basic_download(self):
        """Test basic download command."""
        parser = create_parser()
        args = parser.parse_args(["download", "ryan-a-bell/SysEngBench"])

        assert args.command == "download"
        assert args.dataset == "ryan-a-bell/SysEngBench"
        assert args.split == "test"

    def test_download_with_options(self):
        """Test download with options."""
        parser = create_parser()
        args = parser.parse_args([
            "download", "dataset/name",
            "-o", "/custom/path",
            "--split", "train",
        ])

        assert str(args.output) == "/custom/path"
        assert args.split == "train"


class TestConvertCommand:
    """Tests for convert command parsing."""

    def test_basic_convert(self):
        """Test basic convert command."""
        parser = create_parser()
        args = parser.parse_args(["convert", "input.csv"])

        assert args.command == "convert"
        assert str(args.input) == "input.csv"
        assert args.model == "gpt-4o"

    def test_convert_with_options(self):
        """Test convert with options."""
        parser = create_parser()
        args = parser.parse_args([
            "convert", "input.csv",
            "-o", "output.csv",
            "--model", "gpt-4-turbo",
            "--threshold", "8",
            "--prompt", "custom_prompt",
        ])

        assert str(args.output) == "output.csv"
        assert args.model == "gpt-4-turbo"
        assert args.threshold == 8
        assert args.prompt == "custom_prompt"


class TestJudgeCommand:
    """Tests for judge command parsing."""

    def test_basic_judge(self):
        """Test basic judge command."""
        parser = create_parser()
        args = parser.parse_args(["judge", "responses.json"])

        assert args.command == "judge"
        assert args.provider == "ollama"
        assert args.prompt == "multi_dimensional"

    def test_judge_with_options(self):
        """Test judge with options."""
        parser = create_parser()
        args = parser.parse_args([
            "judge", "responses.json",
            "--provider", "openai",
            "--model", "gpt-4o",
            "--temperature", "0.5",
            "--max-tokens", "4096",
            "--prompt", "chain_of_thought",
        ])

        assert args.provider == "openai"
        assert args.model == "gpt-4o"
        assert args.temperature == 0.5
        assert args.max_tokens == 4096
        assert args.prompt == "chain_of_thought"


class TestAnalyzeCommand:
    """Tests for analyze command parsing."""

    def test_basic_analyze(self):
        """Test basic analyze command."""
        parser = create_parser()
        args = parser.parse_args(["analyze", "bias", "results/"])

        assert args.command == "analyze"
        assert args.type == "bias"

    def test_analyze_types(self):
        """Test different analysis types."""
        parser = create_parser()

        for analysis_type in ["bias", "compare", "all"]:
            args = parser.parse_args(["analyze", analysis_type, "input/"])
            assert args.type == analysis_type


class TestPromptsCommand:
    """Tests for prompts command parsing."""

    def test_basic_prompts(self):
        """Test basic prompts command."""
        parser = create_parser()
        args = parser.parse_args(["prompts"])

        assert args.command == "prompts"
        assert args.category is None

    def test_prompts_with_category(self):
        """Test prompts with category."""
        parser = create_parser()
        args = parser.parse_args(["prompts", "judge"])

        assert args.category == "judge"

    def test_prompts_show(self):
        """Test prompts show option."""
        parser = create_parser()
        args = parser.parse_args(["prompts", "--show", "multi_dimensional"])

        assert args.show == "multi_dimensional"


class TestConfigCommand:
    """Tests for config command parsing."""

    def test_basic_config(self):
        """Test basic config command."""
        parser = create_parser()
        args = parser.parse_args(["config"])

        assert args.command == "config"
        assert args.action == "show"

    def test_config_actions(self):
        """Test config actions."""
        parser = create_parser()

        for action in ["show", "init", "path"]:
            args = parser.parse_args(["config", action])
            assert args.action == action


class TestApp:
    """Tests for app function."""

    def test_no_command_shows_help(self):
        """Test that no command shows help and returns 0."""
        result = app([])
        assert result == 0

    def test_prompts_command(self):
        """Test prompts command runs successfully."""
        result = app(["prompts"])
        assert result == 0

    def test_config_show(self):
        """Test config show command."""
        result = app(["config", "show"])
        assert result == 0

    def test_config_path(self):
        """Test config path command."""
        result = app(["config", "path"])
        assert result == 0
