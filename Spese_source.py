import plistlib
import uuid

def uid():
    return str(uuid.uuid4()).upper()

# UUIDs for grouping
if_group = uid()
menu_group = uid()

# Output UUIDs for actions (to reference their output as variables)
uuid_shortcut_input = uid()
uuid_get_amount = uid()
uuid_get_merchant = uid()
uuid_ask_merchant = uid()
uuid_ask_amount = uid()
uuid_set_importo_auto = uid()
uuid_set_esercente_auto = uid()
uuid_set_importo_manual = uid()
uuid_set_esercente_manual = uid()
uuid_menu = uid()
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

def make_var_ref(output_uuid, output_name, agg_type=None):
    """Create a variable reference to a previous action's output"""
    ref = {
        "OutputUUID": output_uuid,
        "Type": "ActionOutput",
        "OutputName": output_name,
    }
    if agg_type:
        ref["Aggrandizements"] = agg_type
    return ref

def make_token_string(template, attachments):
    """Create a WFTextTokenString with variable references"""
    return {
        "Value": {
            "string": template,
            "attachmentsByRange": attachments,
        },
        "WFSerializationType": "WFTextTokenString",
    }

# U+FFFC is the object replacement character used as placeholder
P = "\ufffc"

actions = []

# ============================================
# ACTION 0: Comment
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
    "WFWorkflowActionParameters": {
        "WFCommentActionText": "Spese Tracker - Logga automaticamente pagamenti Apple Pay e manuali"
    }
})

# ============================================
# ACTION 1: Get Shortcut Input (Count to check if input exists)
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.count",
    "WFWorkflowActionParameters": {
        "Input": {
            "Value": {
                "Type": "ExtensionInput",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_shortcut_input,
    }
})

# ============================================
# ACTION 2: IF - Shortcut Input has any value
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
    "WFWorkflowActionParameters": {
        "GroupingIdentifier": if_group,
        "WFControlFlowMode": 0,  # IF
        "WFCondition": 2,  # "is greater than"
        "WFNumberValue": "0",
        "WFInput": {
            "Value": {
                "Type": "ActionOutput",
                "OutputUUID": uuid_shortcut_input,
                "OutputName": "Count",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# ---- INSIDE IF (Apple Pay triggered) ----

# Get Amount from Shortcut Input
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.detect.number",
    "WFWorkflowActionParameters": {
        "WFInput": {
            "Value": {
                "Type": "ExtensionInput",
                "Aggrandizements": [{"PropertyName": "amount", "Type": "WFContentItemPropertyName"}]
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_get_amount,
    }
})

# Set Variable importo (auto)
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
    "WFWorkflowActionParameters": {
        "WFVariableName": "importo",
        "WFInput": {
            "Value": {
                "Type": "ActionOutput",
                "OutputUUID": uuid_get_amount,
                "OutputName": "Number",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# Get Merchant from Shortcut Input
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
    "WFWorkflowActionParameters": {
        "WFTextActionText": {
            "Value": {
                "string": P,
                "attachmentsByRange": {
                    "{0, 1}": {
                        "Type": "ExtensionInput",
                        "Aggrandizements": [{"PropertyName": "merchant", "Type": "WFContentItemPropertyName"}]
                    }
                }
            },
            "WFSerializationType": "WFTextTokenString",
        },
        "UUID": uuid_get_merchant,
    }
})

# Set Variable esercente (auto)
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
    "WFWorkflowActionParameters": {
        "WFVariableName": "esercente",
        "WFInput": {
            "Value": {
                "Type": "ActionOutput",
                "OutputUUID": uuid_get_merchant,
                "OutputName": "Text",
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# ============================================
# OTHERWISE (manual trigger)
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
    "WFWorkflowActionParameters": {
        "GroupingIdentifier": if_group,
        "WFControlFlowMode": 1,  # OTHERWISE
    }
})

# Ask for Merchant
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.ask",
    "WFWorkflowActionParameters": {
        "WFAskActionPrompt": "Esercente / Descrizione?",
        "WFInputType": "Text",
        "UUID": uuid_ask_merchant,
    }
})

# Set Variable esercente (manual)
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

# Ask for Amount
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.ask",
    "WFWorkflowActionParameters": {
        "WFAskActionPrompt": "Importo?",
        "WFInputType": "Number",
        "UUID": uuid_ask_amount,
    }
})

# Set Variable importo (manual)
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
# END IF
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
    "WFWorkflowActionParameters": {
        "GroupingIdentifier": if_group,
        "WFControlFlowMode": 2,  # END IF
    }
})

# ============================================
# CATEGORY - Choose from Menu
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.choosefrommenu",
    "WFWorkflowActionParameters": {
        "GroupingIdentifier": menu_group,
        "WFControlFlowMode": 0,  # MENU START
        "WFMenuPrompt": "Categoria?",
        "WFMenuItems": categories,
    }
})

# Each menu case
for cat in categories:
    # Menu case header
    actions.append({
        "WFWorkflowActionIdentifier": "is.workflow.actions.choosefrommenu",
        "WFWorkflowActionParameters": {
            "GroupingIdentifier": menu_group,
            "WFControlFlowMode": 1,  # MENU CASE
            "WFMenuItemTitle": cat,
        }
    })
    # Set categoria variable
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

# End menu
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.choosefrommenu",
    "WFWorkflowActionParameters": {
        "GroupingIdentifier": menu_group,
        "WFControlFlowMode": 2,  # MENU END
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
# GET VARIABLES for text composition
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
# BUILD CSV LINE
# ============================================
# Format: Data,Ora,Esercente,Categoria,Importo
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
notif_template = f"Spesa registrata: €{P} - {P}"
notif_attachments = {
    "{19, 1}": {
        "Type": "ActionOutput",
        "OutputUUID": uuid_get_importo,
        "OutputName": "Variable",
    },
    "{23, 1}": {
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
        "WFWorkflowIconStartColor": 463140863,  # Green
        "WFWorkflowIconGlyphNumber": 59470,  # Money/wallet icon
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
    ],
    "WFWorkflowTypes": ["NCWidget", "WatchKit"],
    "WFWorkflowActions": actions,
    "WFWorkflowImportQuestions": [],
}

# Write as binary plist (standard .shortcut format)
output_path = "Spese.shortcut"
with open(output_path, "wb") as f:
    plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)

print(f"Shortcut creato: {output_path}")
print(f"Azioni totali: {len(actions)}")
