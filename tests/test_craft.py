"""Tests for the Craft REST API integration."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from voice_memo_summarizer.craft import (
    create_subpage,
    find_meetings_document,
    insert_content,
    upload_to_craft,
)


def _mock_response(json_data: dict, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=json_data,
        request=httpx.Request("GET", "https://test"),
    )


class TestFindMeetingsDocument:
    def test_finds_meetings_by_title(self) -> None:
        client = MagicMock()
        client.get.return_value = _mock_response(
            {
                "items": [
                    {"id": "doc-1", "title": "Notes", "isDeleted": False},
                    {"id": "doc-2", "title": "Meetings", "isDeleted": False},
                ]
            }
        )

        result = find_meetings_document(client)
        assert result == "doc-2"
        client.get.assert_called_once_with("/documents")

    def test_skips_deleted_documents(self) -> None:
        client = MagicMock()
        client.get.return_value = _mock_response(
            {
                "items": [
                    {"id": "doc-1", "title": "Meetings", "isDeleted": True},
                ]
            }
        )

        with pytest.raises(RuntimeError, match="No 'Meetings' document found"):
            find_meetings_document(client)

    def test_raises_when_not_found(self) -> None:
        client = MagicMock()
        client.get.return_value = _mock_response({"items": []})

        with pytest.raises(RuntimeError, match="No 'Meetings' document found"):
            find_meetings_document(client)


class TestCreateSubpage:
    def test_creates_page_block(self) -> None:
        client = MagicMock()
        client.post.return_value = _mock_response(
            {"items": [{"id": "new-page-id", "type": "page"}]}
        )

        result = create_subpage(client, "parent-id", "2026-03-17 Standup")
        assert result == "new-page-id"

        call_json = client.post.call_args.kwargs["json"]
        assert call_json["blocks"][0]["type"] == "page"
        assert call_json["blocks"][0]["markdown"] == "2026-03-17 Standup"
        assert call_json["position"]["pageId"] == "parent-id"


class TestInsertContent:
    def test_inserts_markdown(self) -> None:
        client = MagicMock()
        client.post.return_value = _mock_response({"items": [{"id": "block-1"}]})

        insert_content(client, "page-id", "## Summary\nContent here.")

        call_json = client.post.call_args.kwargs["json"]
        assert call_json["markdown"] == "## Summary\nContent here."
        assert call_json["position"]["pageId"] == "page-id"


class TestUploadToCraft:
    @patch.dict(
        "os.environ",
        {"CRAFT_API_URL": "https://craft.test/api/v1", "CRAFT_API_KEY": "test-key"},
    )
    @patch("voice_memo_summarizer.craft.httpx.Client")
    def test_full_flow(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        # GET /documents
        mock_client.get.return_value = _mock_response(
            {"items": [{"id": "meetings-id", "title": "Meetings", "isDeleted": False}]}
        )
        # POST /blocks (create subpage, then insert content)
        mock_client.post.return_value = _mock_response({"items": [{"id": "new-page"}]})

        result = upload_to_craft("Team Standup", "## Summary\nWe discussed X.")
        assert "Team Standup" in result
        assert mock_client.get.call_count == 1
        assert mock_client.post.call_count == 2

    @patch.dict("os.environ", {}, clear=True)
    def test_raises_without_env_vars(self) -> None:
        with pytest.raises(RuntimeError, match="CRAFT_API_URL"):
            upload_to_craft("Title", "Content")
