import os
from pathlib import Path

from mtt.types import CaptionModelType as ModelType, LangType
from mtt.utils.caption_utils import caption_explain, chat_output_to_text

_DEFAULT_SUB_PROMPT: dict[LangType, str] = {
    "eng": "Describe this image in detail.",
    "kor": "이 이미지를 자세히 설명해줘.",
}


class CaptionExplanerService:
    def __init__(self, model_name:ModelType, api_key=None):
        self.model_name: ModelType=model_name
        self.api_key=api_key

    def to_text(self, input_path: str | Path, sub_prompt=None, markdown=True, lang: LangType = "eng") -> str:
        if sub_prompt is None:
            sub_prompt = _DEFAULT_SUB_PROMPT.get(lang, _DEFAULT_SUB_PROMPT["eng"])
        result = caption_explain(input_path, model_name=self.model_name, api_key=self.api_key, sub_prompt=sub_prompt)
        return chat_output_to_text(result, model_name=self.model_name, markdown=markdown)