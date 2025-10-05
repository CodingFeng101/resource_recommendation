from backend.common.core.llm.response_getter import ResponseGetterFactory
from ..chains.extraction_chain import run_extraction_chain


class AIExecutor:
    def __init__(self):
        self.response_getter_factory = ResponseGetterFactory()

    async def execute(self, module_executor, **kwargs):
        # 内部导入，避免循环
        from ...module.kg_constructor import SemanticKGConstructor
        ai_response_getter = self.response_getter_factory.create()  # rely on the parameter in the config.py
        # 以三个模块执行器的对象类型为判断依据，决定执行哪个chain
        # llm_parameter所决定的各类response_getter，由对应的chain执行工厂方法。
        if isinstance(module_executor, SemanticKGConstructor):
            return await run_extraction_chain(ai_response_getter=ai_response_getter, **kwargs)  # 这里还需要传入ai_response_getter
        else:
            pass
