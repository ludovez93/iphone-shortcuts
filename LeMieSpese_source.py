import plistlib
import uuid

def uid():
    return str(uuid.uuid4()).upper()

uuid_get_file = uid()

actions = []

# ============================================
# GET FILE: Spese.txt from iCloud
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.documentpicker.open",
    "WFWorkflowActionParameters": {
        "WFFileStorageService": "iCloud",
        "WFFilePath": "Shortcuts/Spese.txt",
        "WFGetFilePath": "Shortcuts/Spese.txt",
        "WFFileNotFound": 1,  # Don't show error if not found
        "UUID": uuid_get_file,
    }
})

# ============================================
# QUICK LOOK: Show the file content
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.previewdocument",
    "WFWorkflowActionParameters": {
        "WFInput": {
            "Value": {
                "Type": "ActionOutput",
                "OutputUUID": uuid_get_file,
                "OutputName": "File",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# ============================================
# BUILD SHORTCUT PLIST
# ============================================
shortcut = {
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowClientVersion": "2702.0.4",
    "WFWorkflowName": "Le mie Spese",
    "WFWorkflowIcon": {
        "WFWorkflowIconStartColor": 4274264319,  # Orange
        "WFWorkflowIconGlyphNumber": 59470,  # Wallet icon
    },
    "WFWorkflowInputContentItemClasses": [],
    "WFWorkflowTypes": ["NCWidget", "WatchKit"],
    "WFWorkflowActions": actions,
    "WFWorkflowImportQuestions": [],
}

output_path = "LeMieSpese.shortcut"
with open(output_path, "wb") as f:
    plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)

print(f"Shortcut creato: {output_path}")
print(f"Azioni totali: {len(actions)}")
