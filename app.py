
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# Load the API key from the .env file
load_dotenv()

# Configure the Streamlit page
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS for a colorful interface
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f3ff, #e0f2fe);
}
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    color: #4338ca;
}
.subtitle {
    text-align: center;
    color: #475569;
    font-size: 17px;
}
div.stButton > button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
    width: 100%;
}
div.stButton > button:hover {
    color: white;
    border: 1px solid #4338ca;
}
.result-card {
    background-color: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #ddd6fe;
}
</style>
""", unsafe_allow_html=True)

# Application heading
st.markdown(
    '<div class="main-title">✈️ AI Travel Planner</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Plan smarter trips with Google Gemini AI</div>',
    unsafe_allow_html=True
)

st.write("")
st.info(
    "Explore how Zero-Shot, Few-Shot, and "
    "Structured Reasoning prompts change AI travel plans."
)

# Sidebar information
with st.sidebar:
    st.title("🌍 About Project")
    st.write(
        "This project compares three AI prompting "
        "techniques using the Google Gemini API."
    )
    st.markdown("### 🧠 Techniques")
    st.write("1. Zero-Shot Prompting")
    st.write("2. Few-Shot Prompting")
    st.write("3. Structured Reasoning Prompting")
    st.markdown("---")
    st.caption("AI Travel Planner | Python + Streamlit + Gemini")

# Travel preference form
st.header("🧳 Customize Your Trip")

with st.form("travel_form"):
    col1, col2 = st.columns(2)

    with col1:
        destination = st.text_input(
            "📍 Destination",
            placeholder="e.g. Istanbul, Turkey"
        )

        days = st.number_input(
            "📅 Trip Duration (days)",
            min_value=1,
            max_value=30,
            value=3
        )

        budget = st.number_input(
            "💰 Total Budget",
            min_value=1,
            value=100000,
            step=5000
        )

        currency = st.selectbox(
            "💱 Budget Currency",
            ["PKR", "USD", "EUR", "GBP", "SAR"]
        )

    with col2:
        travelers = st.number_input(
            "👥 Number of Travelers",
            min_value=1,
            max_value=20,
            value=2
        )

        travel_style = st.selectbox(
            "🎒 Travel Style",
            [
                "Adventure",
                "Family Vacation",
                "Luxury",
                "Budget Friendly",
                "Cultural and Historical",
                "Relaxation",
                "Food and Shopping"
            ]
        )

        preferences = st.text_area(
            "✨ Additional Preferences",
            placeholder=(
                "e.g. beaches, local food, "
                "historical places, nature"
            )
        )

    submitted = st.form_submit_button(
        "✨ Generate & Compare Travel Plans"
    )

# Prompt construction
def create_prompt(technique, destination, days, budget,
                  currency, travelers, travel_style, preferences):

    common_task = f"""
Create a personalized travel itinerary using these details:

Destination: {destination}
Duration: {days} days
Total budget: {budget} {currency}
Number of travelers: {travelers}
Travel style: {travel_style}
Additional preferences: {preferences or "No extra preferences"}

Requirements:
- Suggest a practical day-by-day itinerary.
- Include morning, afternoon, and evening activities.
- Estimate accommodation, food, transport, and activity costs.
- Keep the total estimated cost within the given budget if possible.
- Explain when the budget may be insufficient.
- Suggest transport and food options.
- Mention useful travel and safety tips.
- Clearly label costs as estimates, not confirmed prices.
- Do not invent live bookings or guarantee current opening hours.
- State when details should be verified before travel.
- Make the plan clear and easy to follow.
"""

    if technique == "Zero-Shot Prompting":
        return f"""
You are a helpful AI travel planner.
Create a personalized travel itinerary for the user.

{common_task}

Organize the answer with headings and bullet points.
"""

    elif technique == "Few-Shot Prompting":
        return f"""
You are an expert travel planner. Follow the style and
format shown in these examples.

Example 1:
Input: 1 day in Lahore, cultural trip, budget PKR 5000.
Output:
Day 1:
Morning - Visit a historical landmark.
Afternoon - Explore local food and cultural attractions.
Evening - Enjoy a local market.
Budget: Provide estimated food, transport, and entry costs.
Explain that costs depend on current prices.

Example 2:
Input: 2 days in a city, family vacation.
Output:
Day 1: Family-friendly attractions and a relaxed lunch.
Day 2: Local sightseeing, food, and shopping.
Include a daily schedule, approximate costs, and practical tips.

Now create a NEW plan for the actual user.
Do not copy the examples as the answer.

{common_task}

Follow the example format, but customize every suggestion
for the requested destination and preferences.
"""

    else:
        return f"""
You are a structured AI travel-planning assistant.

Plan the trip by applying these explicit planning criteria:
1. Match activities to the destination and travel style.
2. Distribute activities sensibly across the trip duration.
3. Estimate major expenses and compare their sum with the budget.
4. Consider travel time, practical routes, and rest breaks.
5. Respect the traveler's preferences.
6. Identify uncertainties and details that need verification.

Do not provide hidden internal reasoning. Give a concise
summary of the planning decisions and the resulting itinerary.

{common_task}

Use this output structure:
1. Trip Overview
2. Planning Summary
3. Day-by-Day Itinerary
4. Estimated Budget Breakdown
5. Transport and Food Suggestions
6. Practical Tips and Important Uncertainties
7. Final Budget Check
"""

# Generate a response from Gemini
def generate_plan(client, model_name, prompt):
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response.text


# Generate and compare all three techniques
if submitted:
    if not destination.strip():
        st.error("Please enter a destination first.")

    else:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            st.error(
                "Gemini API key not found. "
                "Please add GEMINI_API_KEY to your .env file."
            )

        else:
            client = genai.Client(api_key=api_key)

            model_name = "gemini-3.5-flash-lite"

            techniques = [
                "Zero-Shot Prompting",
                "Few-Shot Prompting",
                "Structured Reasoning Prompting"
            ]

            user_details = {
                "destination": destination.strip(),
                "days": days,
                "budget": budget,
                "currency": currency,
                "travelers": travelers,
                "travel_style": travel_style,
                "preferences": preferences.strip()
            }

            st.header("🌟 Your AI-Generated Travel Plans")
            st.caption(
                "All three techniques use the same travel preferences. "
                "Responses may vary between runs."
            )

            results = {}

            for technique in techniques:
                with st.expander(
                    f"🧠 {technique}",
                    expanded=True
                ):
                    with st.spinner(
                        f"Generating {technique} itinerary..."
                    ):
                        try:
                            prompt = create_prompt(
                                technique,
                                destination.strip(),
                                days,
                                budget,
                                currency,
                                travelers,
                                travel_style,
                                preferences.strip()
                            )

                            answer = generate_plan(
                                client,
                                model_name,
                                prompt
                            )

                            results[technique] = answer
                            st.markdown(answer)

                        except Exception as error:
                            st.error(
                                f"Could not generate this plan: {error}"
                            )

            # Save results for download
            if results:
                st.markdown("---")
                st.header("📊 Prompting Techniques Comparison")

                comparison = {
                    "Technique": [
                        "Zero-Shot",
                        "Few-Shot",
                        "Structured Reasoning"
                    ],
                    "Prompt Approach": [
                        "Task instructions only",
                        "Task instructions plus examples",
                        "Explicit planning criteria and output structure"
                    ],
                    "Main Focus": [
                        "Direct response",
                        "Learning the desired format from examples",
                        "Organized, constraint-aware planning"
                    ]
                }

                st.table(comparison)

                st.subheader("🔍 What to Observe")
                st.write(
                    "- **Zero-Shot:** How well does Gemini respond "
                    "without examples?"
                )
                st.write(
                    "- **Few-Shot:** Do examples improve consistency "
                    "and formatting?"
                )
                st.write(
                    "- **Structured Reasoning:** Is the itinerary "
                    "more organized and explicit about the budget?"
                )

                st.caption(
                    "These are expected differences, not guaranteed "
                    "results. Compare the actual generated responses."
                )

                report = (
                    "AI TRAVEL PLANNER - PROMPT COMPARISON\n"
                    f"Destination: {destination}\n"
                    f"Duration: {days} days\n"
                    f"Budget: {budget} {currency}\n"
                    f"Travelers: {travelers}\n\n"
                )

                for technique, answer in results.items():
                    report += (
                        f"\n{'=' * 50}\n"
                        f"{technique}\n"
                        f"{'=' * 50}\n\n"
                        f"{answer}\n"
                    )

                st.download_button(
                    label="📥 Download All Travel Plans",
                    data=report,
                    file_name="travel_planner_comparison.txt",
                    mime="text/plain"
                )

                st.success(
                    f"Generated {len(results)} out of "
                    f"{len(techniques)} travel plans."
                )

st.markdown("---")
st.caption(
    "Academic project: AI Travel Planner Using Gemini Prompting Techniques"
)
