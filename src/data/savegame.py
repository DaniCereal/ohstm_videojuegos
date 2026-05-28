import json
from pathlib import Path


SAVE_PATH = Path(__file__).parent / "savegame.json"

MAX_LIVES = 3
DEFAULT_ROOM = (1, 1)
DEFAULT_ENTRY_SIDE = "left"


def default_save():
    return {
        "room": list(DEFAULT_ROOM),
        "entry_side": DEFAULT_ENTRY_SIDE,
        "score": 0,
        "lives": MAX_LIVES,
        "has_checkpoint": False,
        "daedalus_dialogue_complete": False,
    }


def load_save():
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)

        room = data.get("room", DEFAULT_ROOM)
        if len(room) != 2:
            room = DEFAULT_ROOM

        return {
            "room": (int(room[0]), int(room[1])),
            "entry_side": data.get("entry_side", DEFAULT_ENTRY_SIDE),
            "score": int(data.get("score", 0)),
            "lives": int(data.get("lives", MAX_LIVES)),
            "has_checkpoint": bool(data.get("has_checkpoint", False)),
            "daedalus_dialogue_complete": bool(
                data.get("daedalus_dialogue_complete", False)
            ),
        }
    except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
        data = default_save()
        save_game(
            data["room"],
            data["entry_side"],
            data["score"],
            data["lives"],
            data["has_checkpoint"]
        )
        return load_save()


def save_game(
    room,
    entry_side,
    score=0,
    lives=MAX_LIVES,
    has_checkpoint=True,
    daedalus_dialogue_complete=False,
):
    data = {
        "room": [int(room[0]), int(room[1])],
        "entry_side": entry_side,
        "score": int(score),
        "lives": int(lives),
        "has_checkpoint": bool(has_checkpoint),
        "daedalus_dialogue_complete": bool(daedalus_dialogue_complete),
    }

    with open(SAVE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def reset_save():
    data = default_save()
    save_game(
        data["room"],
        data["entry_side"],
        data["score"],
        data["lives"],
        data["has_checkpoint"]
    )
    return load_save()
