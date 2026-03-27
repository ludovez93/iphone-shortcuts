import plistlib
import uuid

def uid():
    return str(uuid.uuid4()).upper()

# Action output UUIDs
uuid_get_amount_text = uid()
uuid_get_amount_clean = uid()
uuid_get_amount = uid()
uuid_get_merchant = uid()
uuid_replace_cibo = uid()
uuid_replace_trasporti = uid()
uuid_replace_abbigliamento = uid()
uuid_replace_svago = uid()
uuid_replace_bollette = uid()
uuid_replace_altro = uid()
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

def make_replace_action(find_pattern, replace_with, input_uuid, input_name, output_uuid):
    """Replace Text action with regex, case-insensitive."""
    action = {
        "WFWorkflowActionIdentifier": "is.workflow.actions.text.replace",
        "WFWorkflowActionParameters": {
            "UUID": output_uuid,
            "WFReplaceTextFind": find_pattern,
            "WFReplaceTextReplace": replace_with,
            "WFReplaceTextRegularExpression": True,
            "WFReplaceTextCaseSensitive": False,
            "WFInput": make_token_string("\ufffc", {
                "{0, 1}": make_attachment(input_uuid, input_name),
            }),
        }
    }
    return action

P = "\ufffc"

actions = []

# ============================================
# COMMENT
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
    "WFWorkflowActionParameters": {
        "WFCommentActionText": (
            "Spese Tracker v8 - FULL AUTO\n"
            "Zero tap: importo + esercente da Wallet Transaction,\n"
            "categoria via regex, salva CSV, notifica.\n"
            "Usa Aggrandizements per estrarre Amount/Merchant."
        )
    }
})

# ============================================
# EXTRACT AMOUNT FROM WALLET TRANSACTION (via Aggrandizement)
# Step 1: Get Amount property as text (returns e.g. "€12,50" or "12.50 EUR")
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
                        "Aggrandizements": [
                            {
                                "Type": "WFPropertyVariableAggrandizement",
                                "PropertyName": "Amount",
                            }
                        ],
                    }
                }
            },
            "WFSerializationType": "WFTextTokenString",
        },
        "UUID": uuid_get_amount_text,
    }
})

# Step 2: Strip currency symbols, keep only digits and comma/dot
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.text.replace",
    "WFWorkflowActionParameters": {
        "UUID": uuid_get_amount_clean,
        "WFReplaceTextFind": "[^\\d\\.,]",
        "WFReplaceTextReplace": "",
        "WFReplaceTextRegularExpression": True,
        "WFReplaceTextCaseSensitive": False,
        "WFInput": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_get_amount_text, "Text"),
        }),
    }
})

# Step 3: Convert cleaned text to number
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.detect.number",
    "WFWorkflowActionParameters": {
        "WFInput": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_get_amount_clean, "Replace Text"),
        }),
        "UUID": uuid_get_amount,
    }
})

# SET VARIABLE importo
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
    "WFWorkflowActionParameters": {
        "WFVariableName": "importo",
        "WFInput": {
            "Value": make_attachment(uuid_get_amount, "Number"),
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# ============================================
# EXTRACT MERCHANT FROM WALLET TRANSACTION (via Aggrandizement)
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
                        "Aggrandizements": [
                            {
                                "Type": "WFPropertyVariableAggrandizement",
                                "PropertyName": "Merchant",
                            }
                        ],
                    }
                }
            },
            "WFSerializationType": "WFTextTokenString",
        },
        "UUID": uuid_get_merchant,
    }
})

# SET VARIABLE esercente
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
    "WFWorkflowActionParameters": {
        "WFVariableName": "esercente",
        "WFInput": {
            "Value": make_attachment(uuid_get_merchant, "Text"),
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# ============================================
# REGEX CATEGORY CHAIN
# Each replace takes the merchant text and if it matches
# the keywords, replaces the ENTIRE text with the category.
# If no match, text passes through unchanged.
# Final catch-all replaces anything that's not a category with "Altro".
# ============================================

# 1. Cibo
actions.append(make_replace_action(
    find_pattern="(?i)^.*(bar|ristorante|pizz|mcdonald|burger|sushi|kebab|trattoria|osteria|gelateria|pasticceria|supermercato|conad|coop|lidl|esselunga|carrefour|eurospin|pam|despar|iper|penny|md |aldi|tigre|crai|simply|alimentari|panificio|macelleria|forno|caffe|caffè|starbucks|autogrill|chef|cucina|gastronomia|rosticceria|friggitoria|paninoteca|tavola calda|mensa|food|eat|just eat|deliveroo|glovo).*$",
    replace_with="Cibo",
    input_uuid=uuid_get_merchant,
    input_name="Text",
    output_uuid=uuid_replace_cibo,
))

# 2. Trasporti
actions.append(make_replace_action(
    find_pattern="(?i)^.*(treni|trenitalia|italo|uber|taxi|cabify|bolt|eni |agip|ip |q8|total|shell|autostrad|parking|parcheggio|metro|bus|atm|amt|anm|cotral|flixbus|ryanair|easyjet|alitalia|ita airways|wizz|vueling|aeroporto|airport|stazione|railway|fuel|benzina|diesel|gpl|elettric|ricarica auto|telepass|car2go|enjoy|share).*$",
    replace_with="Trasporti",
    input_uuid=uuid_replace_cibo,
    input_name="Replace Text",
    output_uuid=uuid_replace_trasporti,
))

# 3. Abbigliamento
actions.append(make_replace_action(
    find_pattern="(?i)^.*(zara|h&m|ovs|primark|nike|adidas|decathlon|calzedonia|intimissimi|bershka|pull.bear|stradivarius|mango|uniqlo|terranova|alcott|pittarello|scarpe|footlocker|foot locker|zalando|bonprix|kiabi|subdued|tezenis|golden point|yamamay|camicissima|gutteridge|sartoria|merceria|tessuti).*$",
    replace_with="Abbigliamento",
    input_uuid=uuid_replace_trasporti,
    input_name="Replace Text",
    output_uuid=uuid_replace_abbigliamento,
))

# 4. Svago
actions.append(make_replace_action(
    find_pattern="(?i)^.*(cinema|netflix|spotify|amazon prime|playstation|xbox|steam|nintendo|teatro|stadio|bowling|escape room|disney|dazn|apple tv|youtube|twitch|concerti|concert|museo|mostra|parco|luna park|aquapark|spa|palestra|gym|fitness|crossfit|piscina|sport|hobby|giochi|game|slot|scommess|bet|poker|bingo|lotteria|gratta).*$",
    replace_with="Svago",
    input_uuid=uuid_replace_abbigliamento,
    input_name="Replace Text",
    output_uuid=uuid_replace_svago,
))

# 5. Bollette
actions.append(make_replace_action(
    find_pattern="(?i)^.*(enel|a2a|iren|hera|acea|eni gas|sorgenia|edison|tim|vodafone|wind|tre|fastweb|sky|iliad|ho mobile|very mobile|postemobile|tiscali|linkem|acqua|gas|luce|elettric|fibra|internet|adsl|assicuraz|insurance|generali|allianz|unipol|axa|mutuo|affitto|rent|condominio|imu|tari|tasi|bollo|canone rai|abbonamento).*$",
    replace_with="Bollette",
    input_uuid=uuid_replace_svago,
    input_name="Replace Text",
    output_uuid=uuid_replace_bollette,
))

# 6. Catch-all: anything that's NOT already a category → "Altro"
actions.append(make_replace_action(
    find_pattern="^(?!Cibo$|Trasporti$|Abbigliamento$|Svago$|Bollette$).+$",
    replace_with="Altro",
    input_uuid=uuid_replace_bollette,
    input_name="Replace Text",
    output_uuid=uuid_replace_altro,
))

# SET VARIABLE categoria
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
    "WFWorkflowActionParameters": {
        "WFVariableName": "categoria",
        "WFInput": {
            "Value": make_attachment(uuid_replace_altro, "Replace Text"),
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }
})

# ============================================
# FORMAT DATE — Get Current Date, then format it
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
            "Value": make_attachment(uuid_date, "Current Date"),
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
            "Value": make_attachment(uuid_date, "Current Date"),
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
            "Value": {"Type": "Variable", "VariableName": "importo"},
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_get_importo,
    }
})

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.getvariable",
    "WFWorkflowActionParameters": {
        "WFVariable": {
            "Value": {"Type": "Variable", "VariableName": "esercente"},
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_get_esercente,
    }
})

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.getvariable",
    "WFWorkflowActionParameters": {
        "WFVariable": {
            "Value": {"Type": "Variable", "VariableName": "categoria"},
            "WFSerializationType": "WFTextTokenAttachment",
        },
        "UUID": uuid_get_categoria,
    }
})

# ============================================
# BUILD READABLE LINE: dd/MM HH:mm | Esercente | Categoria | €Importo
# ============================================
# Template: "dd/MM HH:mm | Esercente | Categoria | €Importo"
#            P    P        P           P            P
readable_template = f"{P} {P} | {P} | {P} | \u20ac{P}"
uuid_readable_line = uid()
readable_attachments = {
    "{0, 1}": make_attachment(uuid_format_date, "Formatted Date"),
    "{2, 1}": make_attachment(uuid_format_time, "Formatted Date"),
    "{6, 1}": make_attachment(uuid_get_esercente, "Variable"),
    "{10, 1}": make_attachment(uuid_get_categoria, "Variable"),
    "{15, 1}": make_attachment(uuid_get_importo, "Variable"),
}

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
    "WFWorkflowActionParameters": {
        "WFTextActionText": make_token_string(readable_template, readable_attachments),
        "UUID": uuid_readable_line,
    }
})

# ============================================
# APPEND TO TXT (human-readable, previews on iPhone)
# ============================================
actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.file.append",
    "WFWorkflowActionParameters": {
        "WFFilePath": {
            "Value": {
                "attachmentsByRange": {},
                "string": "Spese.txt",
            },
            "WFSerializationType": "WFTextTokenString",
        },
        "WFInput": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_readable_line, "Text"),
        }),
        "WFAppendOnNewLine": True,
        "WFFileStorageService": "iCloud",
    }
})

# ============================================
# ALSO APPEND CSV (for Excel export)
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

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.file.append",
    "WFWorkflowActionParameters": {
        "WFFilePath": {
            "Value": {
                "attachmentsByRange": {},
                "string": "Spese.csv",
            },
            "WFSerializationType": "WFTextTokenString",
        },
        "WFInput": make_token_string(P, {
            "{0, 1}": make_attachment(uuid_text_line, "Text"),
        }),
        "WFAppendOnNewLine": True,
        "WFFileStorageService": "iCloud",
    }
})

# ============================================
# SHOW NOTIFICATION
# ============================================
notif_template = f"{P} | \u20ac{P} | {P}"
notif_attachments = {
    "{0, 1}": make_attachment(uuid_get_esercente, "Variable"),
    "{4, 1}": make_attachment(uuid_get_importo, "Variable"),
    "{8, 1}": make_attachment(uuid_get_categoria, "Variable"),
}

actions.append({
    "WFWorkflowActionIdentifier": "is.workflow.actions.notification",
    "WFWorkflowActionParameters": {
        "WFNotificationActionBody": make_token_string(notif_template, notif_attachments),
        "WFNotificationActionTitle": "Spesa registrata",
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
