from pathlib import Path


class PointLLMService:
    '''PointLLM(허깅페이스, 8bit 양자화) 기반 3D 모델 -> 텍스트 설명 서비스.

    TODO: PointLLM 모델 로딩/추론 구현 예정.
    '''

    def __init__(self, **kwargs):
        pass

    def to_text(self, input_path: str | Path) -> str:
        raise NotImplementedError("PointLLM service is not implemented yet.")
