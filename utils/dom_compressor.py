from typing import Dict, Any, List

class DOMCompressor:
    def __init__(self):
        # Elements we care about for navigation and interaction
        self.actionable_roles = {
            "link", "button", "textbox", "searchbox", "combobox", 
            "checkbox", "radio", "menuitem", "spinbutton", "slider"
        }
        self.semantic_roles = {
            "heading", "article", "main", "navigation"
        }

    def flatten_and_filter(self, node: Dict[str, Any], elements_list: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Recursively parses the accessibility tree, filtering out irrelevant 
        layout nodes and flattening it into a list of actionable elements.
        """
        if elements_list is None:
            elements_list = []

        if not node:
            return elements_list

        role = node.get("role", "")
        name = node.get("name", "").strip()

        # Only keep elements that have a role we care about and an accessible name
        if role in self.actionable_roles or (role in self.semantic_roles and name):
            elements_list.append({
                "role": role,
                "name": name,
                # In a full implementation, we would inject unique IDs into the DOM 
                # prior to extraction to map LLM actions back to exact elements.
                # For this prototype, we extract the structure.
                "value": node.get("value", "")
            })

        # Recurse through children
        for child in node.get("children", []):
            self.flatten_and_filter(child, elements_list)

        return elements_list

    def compress(self, raw_tree: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the final compressed representation."""
        filtered_elements = self.flatten_and_filter(raw_tree)
        
        # Limit to top ~50 elements to prevent context window bloat
        compressed_elements = filtered_elements[:50] 
        
        return {
            "status": "success",
            "element_count": len(compressed_elements),
            "elements": compressed_elements
        }