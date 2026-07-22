import markdown
from bs4 import BeautifulSoup

def _remove_markdown(md_text:str) -> str:
    html = markdown.markdown(md_text)

    text = BeautifulSoup(html, "html.parser").get_text()
    return text