import plistlib
import uuid

def uid():
    return str(uuid.uuid4()).upper()

menu_group = uid()

# Action output UUIDs
uuid_get_amount = uid()
uuid_get_merchant = uid()
uuid_ask_amount = uid()
uuid_ask_merchant = uid()
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

def make_attachment(output_uuid, output_name):
    return {
        "Type": "ActionOutput",
        "OutputUUID": output_uuid,
        "OutputName": output_name,
    }

P = "\ufffc"

actions = []

# ============================================
# COMMENT
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
    "WFWorkflowActionParameters": {
        "WFCommentActionText": (
            "Spese Tracker v5\n"
            "- Da Wallet: importo e esercente pre-compilati\n"
            "- Manuale: campi vuoti da riempire\n"
            "- Nessun If/Else, zero errori"
        )
    }
})

# ============================================
# EXTRACT AMOUNT FROM SHORTCUT INPUT
# (Empty if launched manually — that's fine)
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.detect.number",
    "WFWorkflowActionParameters": {
        "WFInput": {
            "Value": {
                "Type": "ExtensionInput",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_get_amount,
    }
})

# ============================================
# EXTRACT MERCHANT FROM SHORTCUT INPUT
# (Empty if launched manually — that's fine)
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
    "WFWorkflowActionParameters": {
        "WFTextActionText": {
            "Value": {
                "string": P,
                "attachmentsByRange": {
                    "{0, 1}": {
                        "Type": "ExtensionInput",
                    }
                }
            },
            "WFSerializationType": "WFTextTokenString",
        },
        "UUID": uuid_get_merchant,
    }
})

# ============================================
# ASK ESERCENTE (pre-filled with merchant if from Wallet)
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.ask",
    "WFWorkflowActionParameters": {
        "WFAskActionPrompt": "Esercente?",
        "WFInputType": "Text",
        "WFAskActionDefaultAnswer": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_get_merchant, "Text"),
        }),
        "UUID": uuid_ask_merchant,
    }
})

# SET VARIABLE esercente
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
    "WFWorkflowActionParameters": {
        "WFVariableName": "esercente",
        "WFInput": {
            "Value": make_attachment(uuid_ask_merchant, "Provided Input"),
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# ============================================
# ASK IMPORTO (pre-filled with amount if from Wallet)
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.ask",
    "WFWorkflowActionParameters": {
        "WFAskActionPrompt": "Importo (EUR)?",
        "WFInputType": "Number",
        "WFAskActionDefaultAnswer": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_get_amount, "Number"),
        }),
        "UUID": uuid_ask_amount,
    }
})

# SET VARIABLE importo
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
    "WFWorkflowActionParameters": {
        "WFVariableName": "importo",
        "WFInput": {
            "Value": make_attachment(uuid_ask_amount, "Provided Input"),
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
                "Value": make_attachment(uuid_set_cat[cat], "Text"),
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
            "Value": make_attachment(uuid_date, "Date"),
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
            "Value": make_attachment(uuid_date, "Date"),
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
    "{0, 1}": make_attachment(uuid_format_date, "Formatted Date"),
    "{2, 1}": make_attachment(uuid_format_time, "Formatted Date"),
    "{4, 1}": make_attachment(uuid_get_esercente, "Variable"),
    "{6, 1}": make_attachment(uuid_get_categoria, "Variable"),
    "{8, 1}": make_attachment(uuid_get_importo, "Variable"),
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
            "Value": make_attachment(uuid_text_line, "Text"),
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
    "{20, 1}": make_attachment(uuid_get_importo, "Variable"),
    "{24, 1}": make_attachment(uuid_get_esercente, "Variable"),
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
    "WFWorkflowHasShortcutInputVariables": True,
    "WFWorkflowName": "Spese",
    "WFWorkflowIcon": {
        "WFWorkflowIconStartColor": 463140863,
        "WFWorkflowIconGlyphNumber": 59470,
    },
    "WFWorkflowInputContentItemClasses": [
        "WFAppStoreAppContentItem",
        "WFArticleContentItem",
        "WFContactContentItem",
        "WFDateContentItem",
        "WFEmailAddressContentItem",
        "WFGenericFileContentItem",
        "WFImageContentItem",
        "WFiTunesProductContentItem",
        "WFLocationContentItem",
        "WFDCMapsLinkContentItem",
        "WFAVAssetContentItem",
        "WFPDFContentItem",
        "WFPhoneNumberContentItem",
        "WFRichTextContentItem",
        "WFSafariWebPageContentItem",
        "WFStringContentItem",
        "WFURLContentItem",
        "WFWalletPassContentItem",
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
