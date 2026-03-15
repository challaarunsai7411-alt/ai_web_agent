import asyncio
import json
from browser.controller import BrowserController
from perception.accessibility_parser import AccessibilityParser
from utils.dom_compressor import DOMCompressor
from agent.decision_engine import DecisionEngine
from agent.executor import ActionExecutor
from perception.dom_observer import DOMObserver
from perception.injector import ElementInjector
from memory.task_memory import TaskMemory
from agent.planner import TaskPlanner
from perception.vision_parser import VisionParser
from utils.speaker import AgentSpeaker
from utils.listener import AgentListener

async def main():
    print("Initializing Autonomous Web Agent...\n")
    
    # Initialize all components exactly once
    memory = TaskMemory() 
    planner = TaskPlanner()
    speaker = AgentSpeaker()
    listener = AgentListener()
    # vision_parser = VisionParser() # <-- Vision disabled for Groq
    browser_ctrl = BrowserController(headless=False)
    parser = AccessibilityParser()
    compressor = DOMCompressor()
    decision_engine = DecisionEngine()

    speaker.speak("I am ready. What would you like me to do on Wikipedia?")
    objective = listener.listen_for_objective()
    
    # 3. FALLBACK IF THE MIC FAILS
    if "Error" in objective:
        speaker.speak("I didn't catch that, so I will search for Computer Science instead.")
        objective = "Type 'Computer Science' into the search bar, submit the search, and click on the first article link in the results."
        
    print(f"🎯 OBJECTIVE: {objective}\n")
    
    # --- SPEAKER 1: Announce planning phase ---
    print("📝 Generating strategic plan...")

    
    plan = await planner.generate_plan(objective)
    
    print("\n=== AGENT CHECKLIST ===")
    for i, step in enumerate(plan):
        print(f"{i+1}. {step}")
    print("=======================\n")
    
    # Combine the original objective with the new plan for the Decision Engine
    plan_string = "\n".join([f"{i+1}. {step}" for i, step in enumerate(plan)])
    enhanced_objective = f"High-Level Goal: {objective}\n\nStep-by-Step Plan to follow:\n{plan_string}"

    try:
        page = await browser_ctrl.start()
        executor = ActionExecutor(page)
        
        # Start at Wikipedia
        await browser_ctrl.navigate("https://www.wikipedia.org")

        # The Autonomous Loop
        max_steps = 5
        for step in range(max_steps):
            print(f"\n--- STEP {step + 1} ---")
            
            # 1. Observe
            await ElementInjector.inject_ids(page)
            raw_tree = await parser.extract_tree(page)
            page_state = compressor.compress(raw_tree)
            page_state["url"] = page.url
            page_state["title"] = await page.title()

            # --- VISION FALLBACK TRIGGER (Commented out for Groq) ---
            # if len(page_state.get("elements", [])) < 5:
            #     print("🦯 Blind spot detected! Accessibility tree is sparse. Activating Vision Fallback...")
            #     visual_hint = await vision_parser.get_visual_guidance(page, objective)
            #     print(f"👁️ Vision System sees: {visual_hint}")
            #     page_state["visual_hint"] = f"VISION SYSTEM OVERRIDE: {visual_hint}"
            # --------------------------------------------------------
            
            print("⏳ Throttling API to respect free tier limits (waiting 5 seconds)...")
            await asyncio.sleep(5) 
            
            # 2. Reason
            print("🧠 Agent is thinking...")
            past_memory = memory.get_memory_string()
            next_action = await decision_engine.get_next_action(enhanced_objective, page_state, past_memory)
            
            if next_action.get("action") == "error":
                # --- SPEAKER 2: Announce an error ---
                speaker.speak("I encountered an error while thinking.")
                print("Stopping loop due to decision engine error.")
                break

            # --- SPEAKER 3: Read the AI's internal thought aloud ---
            agent_thought = next_action.get("thought", "Taking the next step.")
            print(f"\n🤖 AGENT THOUGHT: {agent_thought}")
            speaker.speak(agent_thought)
            # -------------------------------------------------------

            # 3. Act
            is_done = await executor.execute(next_action, speaker=speaker) # <-- Added 'speaker' parameter
            
            # 4. Remember
            memory.add_action(step + 1, next_action)
            
            if is_done or next_action.get("action") == "done":
                # --- SPEAKER 4: Announce success ---
                speaker.speak("I have successfully completed the objective.")
                break
                
            # 5. Wait for State Transition
            await DOMObserver.wait_for_settled(page)

        print("\n🎉 Task finished or max steps reached. Closing in 10 seconds...")
        await asyncio.sleep(10)

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        # --- SPEAKER 5: Announce critical crash ---
        speaker.speak("A critical error occurred.")
    
    finally:
        await browser_ctrl.close()

if __name__ == "__main__":
    asyncio.run(main())