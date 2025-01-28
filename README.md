# travel_agent

Welcome to TravelAgent! This repo contains an agentic AI implementation of a travel assistant. In the form of a chatbot, users can interact with an LLM that augments responses by dynamically calling out to the Google Places API or the Amadeus API for flight search.

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

And to start up the next.js front-end to interact with the travel agent, navigate to frontend/app and run the following:
```
npm run dev
```

# Potential "WOW" factors to think about building in:

## Personalization at Scale

The ability to "feel" like it knows you better with every interaction, without you needing to explain yourself repeatedly.
The AI can pull from preferences and past interactions (e.g., "You loved hiking in Colorado, so I thought you'd enjoy the trails in Sedona.").

## Seamless Integration

Booking flights, hotels, and activities all from the same interface.
Syncing itineraries with your calendar or travel apps.
Real-Time Assistance:

The ability to adjust on the fly during the trip (e.g., "Your flight was delayed, so I rebooked your airport transfer.").

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

What if the travel agent could reach out to you if something closes unexpectedly, remind you of your upcoming flights, and generally interact with you with real-time information pertinent to your trip? Maybe it could provide you in the moment with any tickets you need? 

Examples including knowing the weather -- what if the assistant reached out to you to recommend an alternative indoor activity for one of the days of your trip? What if the travel assistant knew local news and was updated on everything in your trip location, such as terrorist attacks or one-time scheduled events?


## Random annoying things that I hate 

Finding and putting in my KTN
