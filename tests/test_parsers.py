import pytest
from backend.parsers import merge_results, update_with_httpx

def test_merge_results():
    subfinder = ["a.example.com", "b.example.com", "c.example.com"]
    amass = ["B.example.com", "d.example.com"]
    
    merged = merge_results(subfinder, amass)
    
    assert len(merged) == 4
    assert "a.example.com" in merged
    assert "b.example.com" in merged
    assert "c.example.com" in merged
    assert "d.example.com" in merged
    
    assert "subfinder" in merged["a.example.com"].sources
    assert "amass" not in merged["a.example.com"].sources
    
    assert "subfinder" in merged["b.example.com"].sources
    assert "amass" in merged["b.example.com"].sources

def test_update_with_httpx():
    subfinder = ["a.example.com", "b.example.com"]
    merged = merge_results(subfinder, [])
    
    httpx_results = [
        {
            "input": "a.example.com",
            "status_code": 200,
            "title": "Welcome",
            "host": "1.2.3.4",
            "webserver": "nginx"
        }
    ]
    
    update_with_httpx(merged, httpx_results)
    
    assert merged["a.example.com"].is_alive is True
    assert merged["a.example.com"].status_code == 200
    assert merged["a.example.com"].title == "Welcome"
    assert merged["a.example.com"].ip == "1.2.3.4"
    
    assert merged["b.example.com"].is_alive is None
