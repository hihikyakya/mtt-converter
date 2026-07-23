from typing import Literal

ModeType = Literal["caption", "ocr", "3d-parser", "doc"] # TODO: 나중에 point llm까지 하면 point llm을 추가할듯

LangType = Literal["eng", "kor"]

CaptionModelType=Literal["gpt-4o",
                         "gemini-2.5-flash",
                         "gemini-2.5-pro",
                         "gemini-3.5-flash",
                         "gemini-3.5-pro",
                         "claude-opus-4-8"
                         ]