import os
import google.genai as genai
import anthropic
from openai import OpenAI
from PIL import Image
from pathlib import Path

from mtt.types import CaptionModelType as ModelType
from mtt.utils.tools.document_tools import _remove_markdown
from mtt.utils.tools.image_tools import _image_to_base64


def caption_explain(input_path:str | Path, model_name:ModelType,

                      sub_prompt=os.getenv("SUB_PROMPT"),
                      api_key=None
                      ):
    if "gemini" in model_name.lower():
        image=Image.open(input_path)

        gemini=genai.Client(api_key=api_key) if api_key else genai.Client()

        if sub_prompt:
            result = gemini.models.generate_content(
                model=model_name,
                contents=[
                    image,
                    sub_prompt
                ]
            )
        else:
            result = gemini.models.generate_content(
                model=model_name,
                contents=image
            )
    elif "claude" in model_name.lower():
        media_type, image_b64 = _image_to_base64(input_path)

        claude = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

        result = claude.messages.create(
            model=model_name,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": image_b64},
                    },
                    {"type": "text", "text": sub_prompt or "Describe this image in detail."},
                ],
            }],
        )
    elif "gpt" in model_name.lower():
        media_type, image_b64 = _image_to_base64(input_path)

        gpt = OpenAI(api_key=api_key) if api_key else OpenAI()

        result = gpt.chat.completions.create(
            model=model_name,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": sub_prompt or "Describe this image in detail."},
                    {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_b64}"}},
                ],
            }],
        )
    else:
        raise ValueError("Unprepared or non-existent model")
    return result

def chat_output_to_text(result, model_name:str, markdown=True)-> str:
    _model_name=model_name.lower()
    if "gemini" in _model_name:
        text = result.text
    elif "claude" in _model_name:
        text = next(block.text for block in result.content if block.type == "text")
    elif "gpt" in _model_name:
        text = result.choices[0].message.content
    else:
        raise ValueError("Unprepared or non-existent model")
    return text if markdown else _remove_markdown(text)
