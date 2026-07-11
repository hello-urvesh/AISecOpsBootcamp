# Agentic AI Red Team: First Missions

A beginner friendly practice range for learning how AI agents get attacked. It
has exactly two attacks, each with three levels, and a real local AI behind
everything. Nothing is scripted. When you send a message, a real model reads it
and really decides what to do. You win only when the real AI actually breaks its
rule.

This is meant for people who are brand new to agentic AI security. No jargon, no
confusing buttons. Read a short story, watch the AI work normally, then try to
trick it.

## The two attacks

1. The Overdraft Heist. A bank's AI support assistant can put small refunds back
   on a customer account. Your job is to trick it into handing you a large amount
   it should never approve. This teaches prompt injection that leads to a real
   action.

2. The Loose Lipped Concierge. A hotel's AI concierge secretly holds a staff only
   master keycode it must never share. Your job is to get it to reveal the code.
   This teaches sensitive information disclosure.

## The three levels

- Easy. The AI has no real defense. You learn how the attack works.
- Medium. The AI has been told to protect itself. You have to be clever.
- Hard. A second AI double checks the first one. You have to beat both.

## What you need

- Docker Engine with Compose, or Docker Desktop. On Windows use the WSL 2 engine.
- About 8 GB of memory free for Docker, more is better.
- One local AI model, installed from inside the app on first run.

A GPU is not required, but a small model on CPU can be slow. An 8B model is a good
balance.

## Run it

### Linux

    cd agentic-range-lite
    cp .env.example .env
    docker compose up --build -d
    # open http://localhost:8501

### Windows (PowerShell)

    cd .\agentic-range-lite
    Copy-Item .env.example .env
    docker compose up --build -d
    # open http://localhost:8501

### First run: install a model

Open http://localhost:8501, go to the Home page, and install a model with the
button there. Or run it yourself:

    docker compose exec ollama ollama pull llama3.1:8b
    docker compose exec ollama ollama list

Then reload the page. Pick the model in the left sidebar.

## How to play

1. Pick an attack on the left.
2. Read the story so you know what the AI does and what your goal is.
3. Choose a level.
4. Press "Watch the AI work normally" to see how it behaves with an honest message.
5. Write your own message and press "Send my message to the AI".
6. Read what happened. If you broke the AI's rule, you capture a flag and earn
   points. If not, try the hints and go again.

Points add up into a rank, from Recruit to Elite Red Teamer. Your progress is
saved.

## Why the AI sometimes acts differently each time

The agents are real models, so the same message may not always give the exact
same result, just like a real AI assistant. That is part of learning: reliable
attacks work even when the AI varies. If a model refuses everything or behaves
oddly, try a different model in the sidebar.

## Is this safe

Yes. Everything runs on your machine. There is no real bank, no real hotel, no
real money, and no real keycode. The names and secrets are made up for practice.

## Reset progress

    docker compose down                                   # stop, keep everything
    docker volume rm agentic-range-lite_app-data          # clear scores, keep the model
    docker compose down -v                                # remove everything including the model

## What each attack teaches

The Overdraft Heist shows that when an AI can take real actions, tricking it with
words becomes a way to cause real harm. The defense is to treat everything a user
sends as untrusted data, keep hard limits in code, and review sensitive actions.
