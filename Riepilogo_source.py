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

# UUIDs
uuid_read_file = uid()
uuid_get_text = uid()
uuid_match = uid()
uuid_zero = uid()
uuid_strip_euro = uid()
uuid_fix_comma = uid()
uuid_detect_num = uid()
uuid_get_totale = uid()
uuid_math = uid()
uuid_get_contenuto_final = uid()
uuid_get_totale_final = uid()
uuid_display = uid()
uuid_repeat_group = uid()

actions = []

# ============================================
# COMMENT
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
    "WFWorkflowActionParameters": {
        "WFCommentActionText": (
            "Riepilogo Spese v2 - con TOTALE\n"
            "Legge Spese.txt, somma tutti gli importi €,\n"
            "mostra elenco + totale in fondo."
        )
    }
})

# ============================================
# 1. READ FILE
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.documentpicker.open",
    "WFWorkflowActionParameters": {
        "WFFileStorageService": "iCloud",
        "WFFilePath": make_token_string("Spese.txt", {}),
        "WFGetFilePath": make_token_string("Spese.txt", {}),
        "UUID": uuid_read_file,
    }
})

# ============================================
# 2. GET TEXT FROM FILE
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
    "WFWorkflowActionParameters": {
        "WFTextActionText": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_read_file, "File"),
        }),
        "UUID": uuid_get_text,
    }
})

# ============================================
# 3. MATCH TEXT: find all €amounts (e.g. €16,6 €32,40)
# Uses implicit input from Get Text (previous action)
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.text.match",
    "WFWorkflowActionParameters": {
        "WFMatchTextPattern": "\u20ac[\\d,\\.]+",
        "WFMatchTextCaseSensitive": False,
        "UUID": uuid_match,
    }
})

# ============================================
# 4. SET VARIABLE "contenuto"
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
    "WFWorkflowActionParameters": {
        "WFVariableName": "contenuto",
        "WFInput": {
            "Value": make_attachment(uuid_get_text, "Text"),
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# ============================================
# 5. NUMBER: 0 (initial totale)
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.number",
    "WFWorkflowActionParameters": {
        "WFNumberActionNumber": 0,
        "UUID": uuid_zero,
    }
})

# ============================================
# 6. SET VARIABLE "totale" = 0
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
    "WFWorkflowActionParameters": {
        "WFVariableName": "totale",
        "WFInput": {
            "Value": make_attachment(uuid_zero, "Number"),
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# ============================================
# 7. REPEAT WITH EACH (start) — iterate over matched €amounts
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.repeat.each",
    "WFWorkflowActionParameters": {
        "WFInput": {
            "Value": make_attachment(uuid_match, "Matches"),
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "GroupingIdentifier": uuid_repeat_group,
        "WFControlFlowMode": 0,
    }
})

# --- INSIDE LOOP ---

# 7a. Strip € symbol
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.text.replace",
    "WFWorkflowActionParameters": {
        "UUID": uuid_strip_euro,
        "WFReplaceTextFind": "\u20ac",
        "WFReplaceTextReplace": "",
        "WFReplaceTextRegularExpression": False,
        "WFReplaceTextCaseSensitive": False,
        "WFInput": make_token_string(P, {
            "{0, 1}": {
                "Type": "ActionOutput",
                "OutputUUID": uuid_repeat_group,
                "OutputName": "Repeat Item",
            },
        }),
    }
})

# 7b. Replace , with . (Italian decimal → standard)
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.text.replace",
    "WFWorkflowActionParameters": {
        "UUID": uuid_fix_comma,
        "WFReplaceTextFind": ",",
        "WFReplaceTextReplace": ".",
        "WFReplaceTextRegularExpression": False,
        "WFReplaceTextCaseSensitive": False,
        "WFInput": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_strip_euro, "Replace Text"),
        }),
    }
})

# 7c. Detect number from cleaned text
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.detect.number",
    "WFWorkflowActionParameters": {
        "WFInput": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_fix_comma, "Replace Text"),
        }),
        "UUID": uuid_detect_num,
    }
})

# 7d. Get variable "totale" (becomes implicit input for Math)
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.getvariable",
    "WFWorkflowActionParameters": {
        "WFVariable": {
            "Value": {"Type": "Variable", "VariableName": "totale"},
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_get_totale,
    }
})

# 7e. Math: totale + current number
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.math",
    "WFWorkflowActionParameters": {
        "WFMathOperation": "+",
        "WFMathOperand": {
            "Value": make_attachment(uuid_detect_num, "Number"),
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_math,
    }
})

# 7f. Set variable "totale" = new sum
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
    "WFWorkflowActionParameters": {
        "WFVariableName": "totale",
        "WFInput": {
            "Value": make_attachment(uuid_math, "Calculation Result"),
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# ============================================
# REPEAT WITH EACH (end)
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.repeat.each",
    "WFWorkflowActionParameters": {
        "GroupingIdentifier": uuid_repeat_group,
        "WFControlFlowMode": 2,
    }
})

# --- END LOOP ---

# ============================================
# 8. GET VARIABLES FOR DISPLAY
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.getvariable",
    "WFWorkflowActionParameters": {
        "WFVariable": {
            "Value": {"Type": "Variable", "VariableName": "contenuto"},
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_get_contenuto_final,
    }
})

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.getvariable",
    "WFWorkflowActionParameters": {
        "WFVariable": {
            "Value": {"Type": "Variable", "VariableName": "totale"},
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_get_totale_final,
    }
})

# ============================================
# 9. BUILD DISPLAY TEXT
# ============================================
separator = "\u2500" * 21
display_template = f"{P}\n{separator}\nTOTALE: \u20ac{P}"
# Position of second P:
# P(1) + \n(1) + separator(21) + \n(1) + "TOTALE: €"(9) = 33
display_attachments = {
    "{0, 1}": make_attachment(uuid_get_contenuto_final, "Variable"),
    "{33, 1}": make_attachment(uuid_get_totale_final, "Variable"),
}

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
    "WFWorkflowActionParameters": {
        "WFTextActionText": make_token_string(display_template, display_attachments),
        "UUID": uuid_display,
    }
})

# ============================================
# 10. SHOW RESULT
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.showresult",
    "WFWorkflowActionParameters": {
        "Text": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_display, "Text"),
        }),
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
        "WFWorkflowIconStartColor": 4274264319,
        "WFWorkflowIconGlyphNumber": 59470,
    },
    "WFWorkflowInputContentItemClasses": [],
    "WFWorkflowTypes": ["NCWidget", "WatchKit"],
    "WFWorkflowActions": actions,
    "WFWorkflowImportQuestions": [],
}

with open("Riepilogo.shortcut", "wb") as f:
    plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)

print(f"Shortcut creato: Riepilogo.shortcut")
print(f"Azioni totali: {len(actions)}")
