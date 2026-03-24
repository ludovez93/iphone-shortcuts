import plistlib
import uuid

def uid():
    return str(uuid.uuid4()).upper()

menu_group = uid()

uuid_ask_merchant = uid()
uuid_ask_amount = uid()
uuid_set_cat = {}
categories = ["Cibo", "Trasporti", "Abbigliamento", "Svago", "Bollette", "Altro"]
for cat in categories:
    uuid_set_cat[cat] = uid()
uuid_date = uid()
uuid_format_date = uid()
uuid_format_time = uid()
uuid_text_line = uid()
uuid_get_importo = uid()
uuid_get_esercente = uid()
uuid_get_categoria = uid()

def make_token_string(template, attachments):
    return {
        "Value": {
            "string": template,
            "attachmentsByRange": attachments,
        },
        "WFSerializationType": "WFTextTokenString",
    }

P = "\ufffc"

actions = []

# ============================================
# COMMENT
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
    "WFWorkflowActionParameters": {
        "WFCommentActionText": "Spese Tracker - Registra spese manualmente"
    }
})

# ============================================
# ASK: Esercente
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.ask",
    "WFWorkflowActionParameters": {
        "WFAskActionPrompt": "Esercente / Descrizione?",
        "WFInputType": "Text",
        "UUID": uuid_ask_merchant,
    }
})

# SET VARIABLE: esercente
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
    "WFWorkflowActionParameters": {
        "WFVariableName": "esercente",
        "WFInput": {
            "Value": {
                "Type": "ActionOutput",
                "OutputUUID": uuid_ask_merchant,
                "OutputName": "Provided Input",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# ============================================
# ASK: Importo
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.ask",
    "WFWorkflowActionParameters": {
        "WFAskActionPrompt": "Importo (EUR)?",
        "WFInputType": "Number",
        "UUID": uuid_ask_amount,
    }
})

# SET VARIABLE: importo
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
    "WFWorkflowActionParameters": {
        "WFVariableName": "importo",
        "WFInput": {
            "Value": {
                "Type": "ActionOutput",
                "OutputUUID": uuid_ask_amount,
                "OutputName": "Provided Input",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# ============================================
# CATEGORY - Choose from Menu
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.choosefrommenu",
    "WFWorkflowActionParameters": {
        "GroupingIdentifier": menu_group,
        "WFControlFlowMode": 0,
        "WFMenuPrompt": "Categoria?",
        "WFMenuItems": categories,
    }
})

for cat in categories:
    actions.append({
        "WFWorkflowActionIdentifier": "is.workflow.actions.choosefrommenu",
        "WFWorkflowActionParameters": {
            "GroupingIdentifier": menu_group,
            "WFControlFlowMode": 1,
            "WFMenuItemTitle": cat,
        }
    })
    actions.append({
        "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
        "WFWorkflowActionParameters": {
            "WFTextActionText": cat,
            "UUID": uuid_set_cat[cat],
        }
    })
    actions.append({
        "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
        "WFWorkflowActionParameters": {
            "WFVariableName": "categoria",
            "WFInput": {
                "Value": {
                    "Type": "ActionOutput",
                    "OutputUUID": uuid_set_cat[cat],
                    "OutputName": "Text",
                },
                "WFSerializationType": "WFTextTokenAttachment",
            },
        }
    })

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.choosefrommenu",
    "WFWorkflowActionParameters": {
        "GroupingIdentifier": menu_group,
        "WFControlFlowMode": 2,
    }
})

# ============================================
# FORMAT DATE
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.date",
    "WFWorkflowActionParameters": {
        "WFDateActionMode": "Current Date",
        "UUID": uuid_date,
    }
})

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.format.date",
    "WFWorkflowActionParameters": {
        "WFDateFormatStyle": "Custom",
        "WFDateFormat": "dd/MM/yyyy",
        "WFDate": {
            "Value": {
                "Type": "ActionOutput",
                "OutputUUID": uuid_date,
                "OutputName": "Date",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_format_date,
    }
})

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.format.date",
    "WFWorkflowActionParameters": {
        "WFDateFormatStyle": "Custom",
        "WFDateFormat": "HH:mm",
        "WFDate": {
            "Value": {
                "Type": "ActionOutput",
                "OutputUUID": uuid_date,
                "OutputName": "Date",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_format_time,
    }
})

# ============================================
# GET VARIABLES
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.getvariable",
    "WFWorkflowActionParameters": {
        "WFVariable": {
            "Value": {
                "Type": "Variable",
                "VariableName": "importo",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_get_importo,
    }
})

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.getvariable",
    "WFWorkflowActionParameters": {
        "WFVariable": {
            "Value": {
                "Type": "Variable",
                "VariableName": "esercente",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_get_esercente,
    }
})

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.getvariable",
    "WFWorkflowActionParameters": {
        "WFVariable": {
            "Value": {
                "Type": "Variable",
                "VariableName": "categoria",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_get_categoria,
    }
})

# ============================================
# BUILD CSV LINE: Data,Ora,Esercente,Categoria,Importo
# ============================================
csv_template = f"{P},{P},{P},{P},{P}"
csv_attachments = {
    "{0, 1}": {
        "Type": "ActionOutput",
        "OutputUUID": uuid_format_date,
        "OutputName": "Formatted Date",
    },
    "{2, 1}": {
        "Type": "ActionOutput",
        "OutputUUID": uuid_format_time,
        "OutputName": "Formatted Date",
    },
    "{4, 1}": {
        "Type": "ActionOutput",
        "OutputUUID": uuid_get_esercente,
        "OutputName": "Variable",
    },
    "{6, 1}": {
        "Type": "ActionOutput",
        "OutputUUID": uuid_get_categoria,
        "OutputName": "Variable",
    },
    "{8, 1}": {
        "Type": "ActionOutput",
        "OutputUUID": uuid_get_importo,
        "OutputName": "Variable",
    },
}

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
    "WFWorkflowActionParameters": {
        "WFTextActionText": make_token_string(csv_template, csv_attachments),
        "UUID": uuid_text_line,
    }
})

# ============================================
# APPEND TO FILE
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.file.append",
    "WFWorkflowActionParameters": {
        "WFFilePath": "Shortcuts/Spese.csv",
        "WFInput": {
            "Value": {
                "Type": "ActionOutput",
                "OutputUUID": uuid_text_line,
                "OutputName": "Text",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "WFAppendOnNewLine": True,
        "WFFileAppendService": "iCloud",
    }
})

# ============================================
# SHOW NOTIFICATION
# ============================================
notif_template = f"Spesa registrata: \u20ac{P} - {P}"
notif_attachments = {
    "{20, 1}": {
        "Type": "ActionOutput",
        "OutputUUID": uuid_get_importo,
        "OutputName": "Variable",
    },
    "{24, 1}": {
        "Type": "ActionOutput",
        "OutputUUID": uuid_get_esercente,
        "OutputName": "Variable",
    },
}

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.notification",
    "WFWorkflowActionParameters": {
        "WFNotificationActionBody": make_token_string(notif_template, notif_attachments),
        "WFNotificationActionTitle": "Spese Tracker",
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
    "WFWorkflowName": "Spese",
    "WFWorkflowIcon": {
        "WFWorkflowIconStartColor": 463140863,
        "WFWorkflowIconGlyphNumber": 59470,
    },
    "WFWorkflowInputContentItemClasses": [
        "WFStringContentItem",
        "WFGenericFileContentItem",
    ],
    "WFWorkflowTypes": ["NCWidget", "WatchKit"],
    "WFWorkflowActions": actions,
    "WFWorkflowImportQuestions": [],
}

output_path = "Spese.shortcut"
with open(output_path, "wb") as f:
    plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)

print(f"Shortcut creato: {output_path}")
print(f"Azioni totali: {len(actions)}")
