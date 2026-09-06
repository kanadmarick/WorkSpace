import asyncio
import json
import unittest

import httpx

from router_pipe import Pipe, route_question


class FakePipe(Pipe):
    def __init__(self, classifier_label="chat"):
        super().__init__()
        self.classifier_label = classifier_label
        self.calls = []
        self.unloaded = []

    async def _chat(self, payload):
        self.calls.append(payload)
        if payload["model"] == self.valves.CLASSIFIER_MODEL:
            return {"message": {"content": self.classifier_label}}
        return {"message": {"content": "task response"}}

    async def _unload(self, model):
        self.unloaded.append(model)

    async def _stream_chat(self, payload):
        self.calls.append(payload)
        yield self._sse_delta("task response")
        yield "data: [DONE]\n\n"


class RouterPipeTests(unittest.IsolatedAsyncioTestCase):
    async def test_invalid_classifier_label_falls_back_to_chat(self):
        pipe = FakePipe("unknown label")
        result = await pipe.pipe({"stream": False, "messages": [{"role": "user", "content": "Hello"}]})

        self.assertEqual(result["message"]["content"], "task response")
        self.assertEqual(pipe.calls[-1]["model"], "qwen3:8b")

    async def test_same_category_does_not_unload_model(self):
        pipe = FakePipe("code")
        body = {"chat_id": "one", "stream": False, "messages": [{"role": "user", "content": "Fix this function"}]}

        await pipe.pipe(body)
        await pipe.pipe(body)

        self.assertEqual(pipe.unloaded, [])
        self.assertEqual(pipe._sessions["chat:one"].current_model, "qwen2.5-coder:7b")

    async def test_category_change_unloads_previous_model(self):
        pipe = FakePipe("code")
        body = {"chat_id": "one", "stream": False, "messages": [{"role": "user", "content": "Fix this"}]}
        await pipe.pipe(body)

        pipe.classifier_label = "writing"
        await pipe.pipe({**body, "messages": [{"role": "user", "content": "Rewrite this paragraph"}]})

        self.assertEqual(pipe.unloaded, ["qwen2.5-coder:7b"])
        self.assertEqual(pipe._sessions["chat:one"].current_model, "mistral:7b")

    async def test_task_request_keeps_full_history_and_streams_sse(self):
        pipe = FakePipe("math")
        messages = [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "What is 2 + 2?"},
        ]
        stream = await pipe.pipe({"stream": True, "messages": messages})
        chunks = [chunk async for chunk in stream]

        self.assertEqual(pipe.calls[-1]["messages"], messages)
        self.assertEqual(pipe.calls[-1]["model"], "deepseek-r1:7b")
        self.assertEqual(json.loads(chunks[0][6:])["choices"][0]["delta"]["content"], "task response")
        self.assertEqual(chunks[-1], "data: [DONE]\n\n")

    async def test_missing_task_model_falls_back_to_chat(self):
        pipe = FakePipe("math")

        original_chat = pipe._chat

        async def flaky_chat(payload):
            if payload["model"] == "deepseek-r1:7b":
                request = httpx.Request("POST", "http://localhost:11434/api/chat")
                response = httpx.Response(
                    404,
                    request=request,
                    json={"error": {"message": "model not found"}},
                )
                raise httpx.HTTPStatusError("model not found", request=request, response=response)
            return await original_chat(payload)

        pipe._chat = flaky_chat
        body = {"chat_id": "one", "stream": False, "messages": [{"role": "user", "content": "What is 2 + 2?"}]}

        result = await pipe.pipe(body)

        self.assertEqual(result["message"]["content"], "task response")
        self.assertEqual(pipe._sessions["chat:one"].current_model, "qwen3:8b")

    def test_route_question_prefers_small_models_for_easy_tasks(self):
        quick_code = route_question("Fix this Python bug quickly")
        quick_math = route_question("What is 2 + 2?")
        quick_writing = route_question("Rewrite this paragraph")

        self.assertEqual(quick_code["category"], "code")
        self.assertEqual(quick_code["model"], "qwen2.5:3b")
        self.assertEqual(quick_math["category"], "math")
        self.assertEqual(quick_math["model"], "qwen2.5:3b")
        self.assertEqual(quick_writing["category"], "writing")
        self.assertEqual(quick_writing["model"], "llama3.2:3b")


if __name__ == "__main__":
    unittest.main()
