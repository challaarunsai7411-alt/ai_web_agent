from playwright.async_api import Page

class ActionExecutor:
    def __init__(self, page: Page):
        self.page = page

    async def execute(self, action_dict: dict):
        """Executes the LLM's chosen action in the Playwright browser."""
        action = action_dict.get("action")
        element_id = action_dict.get("element_id")
        
        print(f"\n🤖 AGENT THOUGHT: {action_dict.get('thought')}")
        print(f"🛠️  EXECUTING: {action} on element '{element_id}'")

        try:
            if action == "done":
                print("✅ Agent reports objective is complete!")
                return True
                
            if action == "captcha_detected":
                print("\n🚨 CAPTCHA detected. Please solve it to continue.")
                print("⏳ Pausing agent for 30 seconds to allow manual human verification...")
                await self.page.wait_for_timeout(30000) 
                print("▶️ Resuming autonomous navigation loop...")
                return False

            # Target the element using our custom injected ID!
            target_element = self.page.locator(f'[agent-id="{element_id}"]')

            if action == "click":
                await target_element.wait_for(state="visible", timeout=5000)
                await target_element.click()
                await self.page.wait_for_timeout(2000)

            elif action == "type":
                text_to_type = action_dict.get("value", "")
                await target_element.wait_for(state="visible", timeout=5000)
                await target_element.fill(text_to_type)
                await target_element.press("Enter")
                await self.page.wait_for_timeout(3000)

            else:
                print(f"⚠️ Unknown action: {action}")

            return False

        except Exception as e:
            print(f"❌ Failed to execute {action} on {element_id}: {e}")
            return False