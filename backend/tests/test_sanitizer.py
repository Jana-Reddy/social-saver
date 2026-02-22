"""Tests for URL sanitizer service."""
import pytest
from services.sanitizer import extract_urls, classify_url, sanitize_url, is_valid_url
from models.link import LinkSource


class TestExtractUrls:
    def test_single_instagram_reel(self):
        text = "Check this out! https://www.instagram.com/reel/ABC123xyz/"
        urls = extract_urls(text)
        assert len(urls) == 1
        assert urls[0]["source"] == LinkSource.instagram

    def test_single_twitter(self):
        text = "Great thread https://twitter.com/user/status/12345678"
        urls = extract_urls(text)
        assert len(urls) == 1
        assert urls[0]["source"] == LinkSource.twitter

    def test_x_com_twitter(self):
        text = "https://x.com/elonmusk/status/99999"
        urls = extract_urls(text)
        assert len(urls) == 1
        assert urls[0]["source"] == LinkSource.twitter

    def test_multiple_links_in_message(self):
        text = "Save these: https://www.instagram.com/p/DEF456/ and https://example.com/article"
        urls = extract_urls(text)
        assert len(urls) == 2

    def test_text_plus_link(self):
        text = "Hey can you save this for me? https://medium.com/some-article"
        urls = extract_urls(text)
        assert len(urls) == 1
        assert urls[0]["source"] == LinkSource.web

    def test_no_url_in_message(self):
        text = "Hey how are you doing today?"
        urls = extract_urls(text)
        assert len(urls) == 0

    def test_duplicate_links_deduplicated(self):
        text = "https://example.com https://example.com"
        urls = extract_urls(text)
        assert len(urls) == 1

    def test_trailing_punctuation_stripped(self):
        text = "See https://example.com/article."
        urls = extract_urls(text)
        assert urls[0]["url"] == "https://example.com/article"


class TestClassifyUrl:
    def test_instagram_post(self):
        assert classify_url("https://instagram.com/p/ABC/") == LinkSource.instagram

    def test_instagram_reel(self):
        assert classify_url("https://www.instagram.com/reel/XYZ123/") == LinkSource.instagram

    def test_twitter(self):
        assert classify_url("https://twitter.com/user/status/123") == LinkSource.twitter

    def test_plain_web(self):
        assert classify_url("https://news.ycombinator.com") == LinkSource.web

    def test_invalid(self):
        assert classify_url("not a url") == LinkSource.unknown


class TestSanitizeUrl:
    def test_strips_instagram_tracking(self):
        url = "https://www.instagram.com/reel/ABC/?utm_source=ig_web"
        assert "utm_source" not in sanitize_url(url)

    def test_strips_twitter_params(self):
        url = "https://twitter.com/user/status/123?s=20&t=abc"
        assert "?" not in sanitize_url(url)


class TestIsValidUrl:
    def test_valid_https(self):
        assert is_valid_url("https://example.com") is True

    def test_valid_http(self):
        assert is_valid_url("http://example.com/path") is True

    def test_invalid_no_scheme(self):
        assert is_valid_url("example.com") is False

    def test_empty_string(self):
        assert is_valid_url("") is False
