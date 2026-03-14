from playwright.async_api import Page

class ElementInjector:
    @staticmethod
    async def inject_ids(page: Page):
        """
        Injects unique 'agent-id' attributes into all interactive DOM elements.
        It also modifies the aria-label so the ID appears in the Accessibility Tree.
        """
        script = """
        () => {
            let counter = 0;
            // Select all potentially interactive elements
            const selectors = 'a, button, input, textarea, select, [role="button"], [role="link"], [role="checkbox"]';
            
            document.querySelectorAll(selectors).forEach(el => {
                // Only tag elements that are actually visible on screen
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0 && !el.hasAttribute('agent-id')) {
                    counter++;
                    const elementId = `e${counter}`;
                    
                    // 1. Add the custom attribute for Playwright to target
                    el.setAttribute('agent-id', elementId);
                    
                    // 2. Prepend the ID to the element's accessible name so the LLM can read it
                    const currentName = el.getAttribute('aria-label') || el.innerText || el.value || 'unlabeled';
                    el.setAttribute('aria-label', `[${elementId}] ${currentName}`.trim());
                }
            });
            return counter;
        }
        """
        try:
            print("💉 Injecting unique Element IDs into the DOM...")
            await page.evaluate(script)
        except Exception as e:
            print(f"⚠️ Failed to inject IDs: {e}")