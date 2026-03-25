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
uuid_ask_edit = uid()

actions = []

# ============================================
# READ FILE
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.documentpicker.open",
    "WFWorkflowActionParameters": {
        "WFFileStorageService": "iCloud",
        "WFFilePath": {
            "Value": {"attachmentsByRange": {}, "string": "Shortcuts/Spese.txt"},
            "WFSerializationType": "WFTextTokenString",
        },
        "WFGetFilePath": {
            "Value": {"attachmentsByRange": {}, "string": "Shortcuts/Spese.txt"},
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
# ASK FOR INPUT (editable text field with current content)
# User can read, edit, delete lines, then tap OK to save
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.ask",
    "WFWorkflowActionParameters": {
        "WFAskActionPrompt": "Le tue spese (modifica e premi OK):",
        "WFInputType": "Text",
        "WFAskActionDefaultAnswer": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_get_text, "Text"),
        }),
        "UUID": uuid_ask_edit,
    }
})

# ============================================
# SAVE EDITED TEXT BACK TO FILE (overwrite)
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.file.createfolder",
    "WFWorkflowActionParameters": {},
})

# Use Save File to overwrite
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.documentpicker.save",
    "WFWorkflowActionParameters": {
        "WFFileStorageService": "iCloud",
        "WFFilePath": {
            "Value": {"attachmentsByRange": {}, "string": "Shortcuts/Spese.txt"},
            "WFSerializationType": "WFTextTokenString",
        },
        "WFSaveFileOverwrite": True,
        "WFInput": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_ask_edit, "Provided Input"),
        }),
    }
})

# Actually, let me use a simpler approach - delete file then append
# Remove the createfolder and save actions, use a cleaner method

# Rebuild actions list properly
actions = []

# READ FILE
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.documentpicker.open",
    "WFWorkflowActionParameters": {
        "WFFileStorageService": "iCloud",
        "WFFilePath": {
            "Value": {"attachmentsByRange": {}, "string": "Shortcuts/Spese.txt"},
            "WFSerializationType": "WFTextTokenString",
        },
        "WFGetFilePath": {
            "Value": {"attachmentsByRange": {}, "string": "Shortcuts/Spese.txt"},
            "WFSerializationType": "WFTextTokenString",
        },
        "UUID": uuid_get_file,
    }
})

# GET TEXT
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
    "WFWorkflowActionParameters": {
        "WFTextActionText": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_get_file, "File"),
        }),
        "UUID": uuid_get_text,
    }
})

# ASK - editable text with current content
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.ask",
    "WFWorkflowActionParameters": {
        "WFAskActionPrompt": "Modifica e premi OK per salvare:",
        "WFInputType": "Text",
        "WFAskActionDefaultAnswer": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_get_text, "Text"),
        }),
        "UUID": uuid_ask_edit,
    }
})

# SAVE - overwrite file with edited text
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.documentpicker.save",
    "WFWorkflowActionParameters": {
        "WFFileStorageService": "iCloud",
        "WFFilePath": {
            "Value": {"attachmentsByRange": {}, "string": "Shortcuts/Spese.txt"},
            "WFSerializationType": "WFTextTokenString",
        },
        "WFSaveFileOverwrite": True,
        "WFInput": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_ask_edit, "Provided Input"),
        }),
    }
})

# DONE notification
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.notification",
    "WFWorkflowActionParameters": {
        "WFNotificationActionBody": "Spese aggiornate",
        "WFNotificationActionTitle": "Salvato",
        "WFNotificationActionSound": True,
    }
})

# BUILD
shortcut = {
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowClientVersion": "2702.0.4",
    "WFWorkflowName": "Riepilogo Spese",
    "WFWorkflowIcon": {
        "WFWorkflowIconStartColor": 4274264319,
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
