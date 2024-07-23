import pytest
from fastapi.testclient import TestClient
from main import app, extract_text_from_pdf, ask_llm
import requests
from unittest.mock import patch, Mock


client = TestClient(app)

def create_sample_pdf(file_path):
    from PyPDF2 import PdfWriter
    pdf_writer = PdfWriter()
    pdf_writer.add_blank_page(width=72, height=72)  # Create a blank page
    with open(file_path, 'wb') as f:
        pdf_writer.write(f)

def test_upload_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    create_sample_pdf(pdf_path)
    with open(pdf_path, "rb") as f:
        response = client.post("/upload_pdf/", files={"file": ("sample.pdf", f, "application/pdf")})
    assert response.status_code == 200
    assert "pdf_text" in response.json()


def test_ask_question():
    with patch('main.ask_llm', return_value="This is a test response.") as mock_ask_llm:
        response = client.post("/ask_question/", json={"query": "What is this document about?"})
        assert response.status_code == 200
        assert response.json()["response"] == "This is a test response."
        mock_ask_llm.assert_called_once()

def test_extract_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    create_sample_pdf(pdf_path)
    text = extract_text_from_pdf(pdf_path)
    assert isinstance(text, str)


from unittest.mock import patch, Mock

def test_ask_llm(mocker):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"text": "This is a test response."}]}
    
    mocker.patch('requests.post', return_value=mock_response)
    response = ask_llm("What is this document about?", "Some context from PDF.")
    assert response == "This is a test response."

