from uuid import UUID

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agents.graph import build_agent_graph
from app.core.exceptions import WorkflowNotExecutableError
from app.domain.user import User
from app.domain.workflow_run import WorkflowRun
from app.repositories.workflow_run_repository import WorkflowRunRepositoryProtocol
from app.services.workflow_service import WorkflowService


class WorkflowExecutionService:
    def __init__(
        self,
        workflow_service: WorkflowService,
        workflow_run_repository: WorkflowRunRepositoryProtocol,
    ) -> None:
        self._workflow_service = workflow_service
        self._workflow_run_repository = workflow_run_repository

    async def execute(self, requester: User, workflow_id: UUID, message: str) -> WorkflowRun:
        workflow = await self._workflow_service.get_by_id(requester, workflow_id)

        if not workflow.is_executable():
            raise WorkflowNotExecutableError(workflow.id)

        run = WorkflowRun(workflow_id=workflow.id, input_message=message)
        run = await self._workflow_run_repository.create(run)

        try:
            graph = await build_agent_graph(workflow.llm_model)
            result = await graph.ainvoke(
                {
                    "messages": [
                        SystemMessage(content=workflow.system_prompt),
                        HumanMessage(content=message),
                    ]
                }
            )
            output = result["messages"][-1]
            input_tokens, output_tokens = self._extract_token_usage(output)
            run.mark_completed(str(output.content), input_tokens, output_tokens)
        except Exception as exc:  # noqa: BLE001
            run.mark_failed(str(exc))

        return await self._workflow_run_repository.update(run)

    @staticmethod
    def _extract_token_usage(message: AIMessage) -> tuple[int, int]:
        usage = message.usage_metadata
        if usage is None:
            return 0, 0
        return usage["input_tokens"], usage["output_tokens"]
