from playwright.async_api import Page

class DOMObserver:
    @staticmethod
    async def wait_for_settled(page: Page, quiet_period_ms: int = 1500):
        """
        Injects a JavaScript MutationObserver into the browser.
        It waits until the DOM has stopped changing for a specific amount of time
        before allowing the Python script to continue.
        """
        script = f"""
        () => {{
            return new Promise((resolve) => {{
                let timeout;
                
                // Watch for any changes to the DOM structure or attributes
                const observer = new MutationObserver((mutations) => {{
                    clearTimeout(timeout);
                    // Reset the timer every time the DOM twitches
                    timeout = setTimeout(() => {{
                        observer.disconnect();
                        resolve('dom_settled');
                    }}, {quiet_period_ms});
                }});
                
                observer.observe(document.body, {{
                    childList: true,
                    subtree: true,
                    attributes: true
                }});
                
                // Fallback: If the DOM is already quiet, resolve after the quiet period
                timeout = setTimeout(() => {{
                    observer.disconnect();
                    resolve('no_mutations_detected');
                }}, {quiet_period_ms});
            }});
        }}
        """
        
        try:
            print(f"⏳ Waiting for dynamic page content to settle...")
            # Execute the JS promise in the browser and wait for it to resolve
            await page.evaluate(script)
        except Exception as e:
            print(f"⚠️ DOM Observer warning: {e}")