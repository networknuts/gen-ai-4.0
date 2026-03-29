from dotenv import load_dotenv
from typing import TypedDict
from langchain_openai import ChatOpenAI 
from langgraph.graph import StateGraph, END 

# SETUP THE ENVIRONMENT
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini"
)

# DEFINING OUR STATE
class SupportState(TypedDict):
    user_query: str
    intent: str
    response: str 


# NODE 1: INTENT CLASSIFIER
def classify_intent(state: SupportState):
    prompt = f"""
    Classify the user query into one of these categories:
    - password_reset
    - order_tracking
    - refund 

    Only return the category name.

    User query: {state['user_query']}
    """
    result = llm.invoke(prompt)
    return {"intent": result.content.strip().lower()}

# NODE 2: PASSWORD RESET NODE

def handle_password(state: SupportState):
    return {
        "response": (
            "To reset your pasword, click on 'forgot password'"
            "On the login page and follow the on-screen instructions"
        )
    }

# NODE 3: ORDER TRACKING NODE

def handle_order(state: SupportState):
    return {
        "response": (
            "Please click on 'my orders' under your profile"
            "Click on the order name which you wish to track"
        )
    }

# NODE 4: REFUND NODE

def handle_refund(state: SupportState):
    return {
        "response": (
            "Refund request received, we will perform the refund in 7 days."
        )
    }

# NODE 5: ROUTING NODE
def route_intent(state: SupportState):
    if state["intent"] == "password_reset":
        return "password_node"
    elif state["intent"] == "order_tracking":
        return "order_node"
    elif state["intent"] == "refund":
        return "refund_node"
    else:
        return END 

# BUILDING THE WORKFLOW GRAPH

graph = StateGraph(SupportState)

graph.add_node("classifier", classify_intent)
graph.add_node("password_node", handle_password)
graph.add_node("order_node", handle_order)
graph.add_node("refund_node", handle_refund)

# DECIDE THE ENTRY POINT OF YOUR WORKFLOW

graph.set_entry_point("classifier")

# CONDITION BASED ROUTING
graph.add_conditional_edges("classifier", route_intent)

# EDGES
graph.add_edge("password_node", END)
graph.add_edge("order_node", END)
graph.add_edge("refund_node", END)

app = graph.compile()


# RUN THE APP

user_input = input("QUERY: ")

result = app.invoke({
    "user_query": user_input,
    "intent": "",
    "response": ""
})

print(result['response'])