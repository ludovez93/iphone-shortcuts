import plistlib
import uuid
import requests

def uid():
    return str(uuid.uuid4()).upper()

def make_token_string(template, attachments):
    return {
        "Value": {
            "string": template,
            "attachmentsByRange": attachments,
        },
        "WFSerializationType": "WFTextTokenString",
    }

def make_attachment(output_uuid, output_name):
    return {
        "Type": "ActionOutput",
        "OutputUUID": output_uuid,
        "OutputName": output_name,
    }

P = "\ufffc"

# UUIDs
uuid_find_notes = uid()
uuid_append_note = uid()
uuid_text = uid()

actions = []

# ============================================
# COMMENT
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
    "WFWorkflowActionParameters": {
        "WFCommentActionText": "Test Note - Cerca nota 'Spese' e aggiunge testo"
    }
})

# ============================================
# 1. FIND NOTES - cerca nota con nome "Spese"
# ============================================
# Operator values: 4 = "is" (exact match), 99 = "contains", 8 = "begins with"
# Property: "Name" = titolo della nota
# WFActionParameterFilterPrefix: 1 = all conditions must match
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.filter.notes",
    "WFWorkflowActionParameters": {
        "UUID": uuid_find_notes,
        "WFContentItemFilter": {
            "Value": {
                "WFActionParameterFilterPrefix": 1,
                "WFContentPredicateBoundedDate": False,
                "WFActionParameterFilterTemplates": [
                    {
                        "Property": "Name",
                        "Operator": 4,
                        "String": "Spese",
                        "VariableOverrides": {},
                    },
                ],
            },
            "WFSerializationType": "WFContentPredicateTableTemplate",
        },
        "WFContentItemSortProperty": "Name",
        "WFContentItemSortOrder": "Latest First",
        "WFContentItemLimitNumber": 1,
    },
})

# ============================================
# 2. TEXT - prepara il testo da appendere
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
    "WFWorkflowActionParameters": {
        "WFTextActionText": {
            "Value": {
                "string": "test nota 123",
                "attachmentsByRange": {},
            },
            "WFSerializationType": "WFTextTokenString",
        },
        "UUID": uuid_text,
    }
})

# ============================================
# 3. APPEND TO NOTE - aggiunge testo alla nota trovata
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.appendnote",
    "WFWorkflowActionParameters": {
        "UUID": uuid_append_note,
        "WFNote": {
            "Value": {
                "Type": "ActionOutput",
                "OutputUUID": uuid_find_notes,
                "OutputName": "Notes",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "WFInput": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_text, "Text"),
        }),
    }
})

# ============================================
# 4. SHOW NOTIFICATION
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.notification",
    "WFWorkflowActionParameters": {
        "WFNotificationActionBody": {
            "Value": {
                "string": "Scritto su nota!",
                "attachmentsByRange": {},
            },
            "WFSerializationType": "WFTextTokenString",
        },
        "WFNotificationActionTitle": "Test Note",
        "WFNotificationActionSound": True,
    }
})

# ============================================
# BUILD SHORTCUT PLIST
# ============================================
shortcut = {
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowClientVersion": "2702.0.4",
    "WFWorkflowHasShortcutInputVariables": False,
    "WFWorkflowName": "Test Note",
    "WFWorkflowIcon": {
        "WFWorkflowIconStartColor": 4274264319,  # giallo
        "WFWorkflowIconGlyphNumber": 59163,       # icona nota
    },
    "WFWorkflowInputContentItemClasses": [
        "WFStringContentItem",
    ],
    "WFWorkflowTypes": ["NCWidget", "WatchKit"],
    "WFWorkflowActions": actions,
    "WFWorkflowImportQuestions": [],
}

# Save unsigned
unsigned_path = "test_note.shortcut"
with open(unsigned_path, "wb") as f:
    plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)
print(f"Shortcut creato: {unsigned_path}")
print(f"Azioni totali: {len(actions)}")

# Sign via HubSign
import base64
with open(unsigned_path, "rb") as f:
    raw = f.read()

# Convert binary plist to XML for signing
shortcut_xml = plistlib.dumps(shortcut, fmt=plistlib.FMT_XML).decode("utf-8")

print(f"\nFirma via HubSign...")
resp = requests.post(
    "https://hubsign.routinehub.services/sign",
    json={"shortcut": shortcut_xml},
    timeout=30,
)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    signed_path = "test_note_signed.shortcut"
    with open(signed_path, "wb") as f:
        f.write(resp.content)
    print(f"Firmato e salvato: {signed_path}")
    print(f"Dimensione: {len(resp.content)} bytes")
else:
    print(f"Errore: {resp.text[:500]}")
