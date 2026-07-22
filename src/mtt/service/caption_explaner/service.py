import os
from pathlib import Path

from mtt.types import CaptionModelType as ModelType
from mtt.utils.caption_utils import caption_explain, chat_output_to_text


class CaptionExplanerService:
    def __init__(self, model_name:ModelType, api_key=None):
        self.model_name: ModelType=model_name
        self.api_key=api_key

    def to_text(self, input_path: str | Path, sub_prompt=None, markdown=True) -> str:
        result = caption_explain(input_path, model_name=self.model_name, api_key=self.api_key, sub_prompt=sub_prompt)
        return chat_output_to_text(result, model_name=self.model_name, markdown=markdown)