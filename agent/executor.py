from playwright.async_api import Page

class ActionExecutor:
    def __init__(self, page: Page):
        self.page = page

    # --- NEW: Added 'speaker' to the arguments so the hands can talk! ---
    async def execute(self, action_dict: dict, speaker=None):
        """Executes the LLM's chosen action in the Playwright browser."""
        action = action_dict.get("action")
        element_id = action_dict.get("element_id")
        
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

            # --- NEW: SCROLL ACTION ---
            if action == "scroll":
                print("⏬ Scrolling down the page...")
                # Scroll down by 80% of the viewport height to simulate natural reading
                await self.page.evaluate("window.scrollBy(0, window.innerHeight * 0.8);")
                await self.page.wait_for_timeout(2000)
                return False

            # Target the element using our custom injected ID!
            if element_id:
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

                # --- NEW: READ CONTENT ACTION ---
                elif action == "read_content":
                    await target_element.wait_for(state="visible", timeout=5000)
                    
                    # Extract the raw text from the webpage
                    content = await target_element.inner_text()
                    
                    # Clean up the text (remove massive whitespace gaps)
                    clean_content = " ".join(content.split())
                    
                    # Truncate to 500 characters so it doesn't talk forever
                    preview = clean_content[:500] + ("..." if len(clean_content) > 500 else "")
                    
                    print(f"\n📄 EXTRACTED TEXT:\n{preview}\n")
                    
                    # Read it aloud to the user!
                    if speaker:
                        speaker.speak(f"Here is what the page says: {preview}")
                        
                    await self.page.wait_for_timeout(2000)

                else:
                    print(f"⚠️ Unknown action: {action}")

            return False

        except Exception as e:
            print(f"❌ Failed to execute {action} on {element_id}: {e}")
            return False