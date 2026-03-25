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

# 1. READ FILE
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

# 2. GET TEXT FROM FILE
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
    "WFWorkflowActionParameters": {
        "WFTextActionText": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_get_file, "File"),
        }),
        "UUID": uuid_get_text,
    }
})

# 3. ASK - editable text
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

# 4. DELETE OLD FILE
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.file.delete",
    "WFWorkflowActionParameters": {
        "WFInput": {
            "Value": {
                "Type": "ActionOutput",
                "OutputUUID": uuid_get_file,
                "OutputName": "File",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "WFDeleteFileConfirmDeletion": False,
    }
})

# 5. WRITE NEW FILE (append to non-existing file = create)
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.file.append",
    "WFWorkflowActionParameters": {
        "WFFilePath": {
            "Value": {"attachmentsByRange": {}, "string": "Shortcuts/Spese.txt"},
            "WFSerializationType": "WFTextTokenString",
        },
        "WFInput": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_ask_edit, "Provided Input"),
        }),
        "WFAppendOnNewLine": False,
        "WFFileStorageService": "iCloud",
    }
})

# 6. NOTIFICATION
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.notification",
    "WFWorkflowActionParameters": {
        "WFNotificationActionBody": "Spese aggiornate",
        "WFNotificationActionTitle": "Salvato",
        "WFNotificationActionSound": True,
    }
})

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
