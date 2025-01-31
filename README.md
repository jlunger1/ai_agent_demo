# ai_agent_demo

Welcome to AI agent demo! In the form of a chatbot, users can interact with an LLM that augments responses by dynamically calling out to tools such as the Google Places API.

Other details:
- The conversation for each session is saved in the django database. Future implementations to include use of previous conversations as added context (e.g. "memory")
- Future versions to include a longer list of tools available to the assistant.


## Using the repository

To set up the uv environment run the following:

```
uv venv
uv sync
uv pip install -e .
```

To turn on the django-based backend API endpoint:
```
python manage.py runserver
```

And to start up the next.js front-end to interact with the agent, navigate to frontend/app and run the following:
```
npm run dev
```

# Potential "WOW" factors to think about building in:

## Personalization at Scale

The ability to "feel" like it knows you better with every interaction, without you needing to explain yourself repeatedly.
The AI can pull from preferences and past interactions (e.g., "You loved hiking in Colorado, so I thought you'd enjoy the trails in Sedona.").

## Seamless Integration

By adding more tools and multi-tool interactions, can the assistant feel like a competent human that seamlessly uses tools to acheive goals without user intervention?

## Human-Like Decision-Making

The agent feels like a partner in planning rather than a tool:
It justifies its choices: "This hotel is slightly above your budget, but it’s the top-rated option and right by the beach."
It anticipates concerns: "There’s a cheaper flight option, but it has a long layover. Would you prefer a direct flight?"

## Confidence in Recommendations

Trust is critical when making big decisions like where to stay or what to do. To achieve this, the agent needs to explain decisions, build credibility, balance options.

Implementation ideas:
- pulling more sources, including Reddit, travel blogs, Google search, tripadvisor, official tourism websites
- user content

## Real-Time Information

What if the agent could reach out to you if something changes unexpectedly, remind you of your upcoming reservations, and generally interact with you with real-time information? Maybe it could provide you in the moment with any tickets you need? 

Examples including knowing the weather -- what if the assistant reached out to you to recommend an alternative indoor activity? What if the travel assistant knew local news and was updated on everything in your location, such as terrorist attacks or one-time scheduled events?


## Random annoying things that I hate 

Finding passwords and keys (e.g. inputting my KTN or passport information)
