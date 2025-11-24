import asyncio, json
from self_heal import self_heal

class HybridAI:
    def __init__(self, memory_limit=20):
        self.memory = []
        self.memory_limit = memory_limit
        self.milestones_file = "milestones.json"

    async def generate(self, prompt):
        context = "\n".join(self.memory[-self.memory_limit:])
        try:
            response = await self.call_mistral(prompt, context)
            self.memory.append(f"User: {prompt}")
            self.memory.append(f"AI: {response}")
            self._record_milestone(prompt, response)
            return response
        except Exception as e:
            self_heal(f"HybridAI generate error: {e}")
            return f"(Fallback AI svar: {prompt})"

    async def call_mistral(self, prompt, context):
        await asyncio.sleep(0.1)  # placeholder
        return f"[AI Response] {prompt}"

    def reset_memory(self): self.memory.clear()

    def _record_milestone(self, prompt, response):
        try:
            with open(self.milestones_file, "a") as f:
                json.dump({"prompt": prompt, "response": response}, f)
                f.write("\n")
        except Exception as e:
            self_heal(f"Milestone record failed: {e}")
