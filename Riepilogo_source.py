import plistlib
import uuid

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

uuid_get_file = uid()
uuid_get_text = uid()

actions = []

# ============================================
# GET FILE: Spese.txt from iCloud
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.documentpicker.open",
    "WFWorkflowActionParameters": {
        "WFFileStorageService": "iCloud",
        "WFFilePath": {
            "Value": {
                "attachmentsByRange": {},
                "string": "Shortcuts/Spese.txt",
            },
            "WFSerializationType": "WFTextTokenString",
        },
        "WFGetFilePath": {
            "Value": {
                "attachmentsByRange": {},
                "string": "Shortcuts/Spese.txt",
            },
            "WFSerializationType": "WFTextTokenString",
        },
        "UUID": uuid_get_file,
    }
})

# ============================================
# GET TEXT FROM FILE
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
    "WFWorkflowActionParameters": {
        "WFTextActionText": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_get_file, "File"),
        }),
        "UUID": uuid_get_text,
    }
})

# ============================================
# SHOW RESULT (big readable text)
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.showresult",
    "WFWorkflowActionParameters": {
        "Text": make_token_string(
            f"LE MIE SPESE\n--------------------\n{P}",
            {
                "{34, 1}": make_attachment(uuid_get_text, "Text"),
            }
        ),
    }
})

# ============================================
# BUILD SHORTCUT PLIST
# ============================================
shortcut = {
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowClientVersion": "2702.0.4",
    "WFWorkflowName": "Riepilogo Spese",
    "WFWorkflowIcon": {
        "WFWorkflowIconStartColor": 4274264319,  # Orange
        "WFWorkflowIconGlyphNumber": 59470,
    },
    "WFWorkflowInputContentItemClasses": [],
    "WFWorkflowTypes": ["NCWidget", "WatchKit"],
    "WFWorkflowActions": actions,
    "WFWorkflowImportQuestions": [],
}

output_path = "Riepilogo.shortcut"
with open(output_path, "wb") as f:
    plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)

print(f"Shortcut creato: {output_path}")
print(f"Azioni totali: {len(actions)}")
