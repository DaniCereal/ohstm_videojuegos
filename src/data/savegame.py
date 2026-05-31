import json
from pathlib import Path


SAVE_PATH = Path(__file__).parent / "savegame.json"

MAX_LIVES = 3
DEFAULT_ROOM = (2, 0)
DEFAULT_ENTRY_SIDE = "left"


def default_save():
    return {
        "room": list(DEFAULT_ROOM),
        "safe_room": list(DEFAULT_ROOM),
        "entry_side": DEFAULT_ENTRY_SIDE,
        "score": 0,
        "lives": MAX_LIVES,
        "max_lives": MAX_LIVES,
        "has_checkpoint": False,
        "daedalus_dialogue_complete": False,
        "daedalus_second_dialogue_complete": False,
        "talked_to_zeus": False,
        "hades_dialogue_complete": False,
        "dialogue_progress": {},
        "feather_count": 0,
        "cleared_feather_rooms": [],
        "has_double_jump": False,
        "has_dash": False,
        "has_wall_jump": False,
    }


def load_save():
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)

        room = data.get("room", DEFAULT_ROOM)
        if len(room) != 2:
            room = DEFAULT_ROOM
        safe_room = data.get("safe_room", room)
        if len(safe_room) != 2:
            safe_room = room

        raw_cleared = data.get("cleared_feather_rooms", [])
        cleared = [tuple(r) for r in raw_cleared if isinstance(r, (list, tuple)) and len(r) == 2]
        return {
            "room": (int(room[0]), int(room[1])),
            "safe_room": (int(safe_room[0]), int(safe_room[1])),
            "entry_side": data.get("entry_side", DEFAULT_ENTRY_SIDE),
            "score": int(data.get("score", 0)),
            "lives": int(data.get("lives", MAX_LIVES)),
            "max_lives": int(data.get("max_lives", MAX_LIVES)),
            "has_checkpoint": bool(data.get("has_checkpoint", False)),
            "daedalus_dialogue_complete": bool(
                data.get("daedalus_dialogue_complete", False)
            ),
            "feather_count": int(data.get("feather_count", 0)),
            "cleared_feather_rooms": cleared,
            "has_double_jump": bool(data.get("has_double_jump", False)),
            "has_dash": bool(data.get("has_dash", False)),
            "has_wall_jump": bool(data.get("has_wall_jump", False)),
            "daedalus_second_dialogue_complete": bool(
                data.get("daedalus_second_dialogue_complete", False)
            ),
            "talked_to_zeus": bool(data.get("talked_to_zeus", False)),
            "hades_dialogue_complete": bool(data.get("hades_dialogue_complete", False)),
            "dialogue_progress": dict(data.get("dialogue_progress", {})),
        }
    except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
        data = default_save()
        save_game(
            data["room"],
            data["entry_side"],
            score=data["score"],
            lives=data["lives"],
            max_lives=data["max_lives"],
            has_checkpoint=data["has_checkpoint"],
            safe_room=data["safe_room"],
            daedalus_dialogue_complete=data["daedalus_dialogue_complete"],
            daedalus_second_dialogue_complete=data["daedalus_second_dialogue_complete"],
            talked_to_zeus=data["talked_to_zeus"],
            hades_dialogue_complete=data["hades_dialogue_complete"],
            dialogue_progress=data["dialogue_progress"],
            feather_count=data["feather_count"],
            cleared_feather_rooms=data["cleared_feather_rooms"],
            has_double_jump=data["has_double_jump"],
            has_dash=data["has_dash"],
            has_wall_jump=data["has_wall_jump"],
        )
        return load_save()


def save_game(
    room,
    entry_side,
    score=0,
    lives=MAX_LIVES,
    max_lives=MAX_LIVES,
    has_checkpoint=True,
    safe_room=None,
    daedalus_dialogue_complete=False,
    daedalus_second_dialogue_complete=False,
    talked_to_zeus=False,
    hades_dialogue_complete=False,
    dialogue_progress=None,
    feather_count=0,
    cleared_feather_rooms=None,
    has_double_jump=False,
    has_dash=False,
    has_wall_jump=False,
):
    data = {
        "room": [int(room[0]), int(room[1])],
        "safe_room": [
            int((safe_room or room)[0]),
            int((safe_room or room)[1]),
        ],
        "entry_side": entry_side,
        "score": int(score),
        "lives": int(lives),
        "max_lives": int(max_lives),
        "has_checkpoint": bool(has_checkpoint),
        "daedalus_dialogue_complete": bool(daedalus_dialogue_complete),
        "daedalus_second_dialogue_complete": bool(daedalus_second_dialogue_complete),
        "talked_to_zeus": bool(talked_to_zeus),
        "hades_dialogue_complete": bool(hades_dialogue_complete),
        "dialogue_progress": dict(dialogue_progress or {}),
        "feather_count": int(feather_count),
        "cleared_feather_rooms": [list(r) for r in (cleared_feather_rooms or [])],
        "has_double_jump": bool(has_double_jump),
        "has_dash": bool(has_dash),
        "has_wall_jump": bool(has_wall_jump),
    }

    with open(SAVE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def reset_save():
    data = default_save()
    save_game(
        data["room"],
        data["entry_side"],
        score=data["score"],
        lives=data["lives"],
        max_lives=data["max_lives"],
        has_checkpoint=data["has_checkpoint"],
        safe_room=data["safe_room"],
        daedalus_dialogue_complete=data["daedalus_dialogue_complete"],
        daedalus_second_dialogue_complete=data["daedalus_second_dialogue_complete"],
        talked_to_zeus=data["talked_to_zeus"],
        hades_dialogue_complete=data["hades_dialogue_complete"],
        dialogue_progress=data["dialogue_progress"],
        feather_count=data["feather_count"],
        cleared_feather_rooms=data["cleared_feather_rooms"],
        has_double_jump=data["has_double_jump"],
        has_dash=data["has_dash"],
        has_wall_jump=data["has_wall_jump"],
    )
    return load_save()
