#!/usr/bin/env python3
"""
Shortcut Plist Validator
========================
Validates .shortcut files (binary plist) WITHOUT an iPhone or Mac.

Checks:
1. Plist structure validity (required keys, types)
2. Action identifier validity
3. OutputName correctness for action references
4. UUID referential integrity (all referenced UUIDs exist)
5. attachmentsByRange position correctness (positions match placeholder chars)
6. Control flow integrity (matching GroupingIdentifier start/end)
7. Magic variable validity (CurrentDate, Clipboard, etc.)
8. Aggrandizement structure validity

Usage:
    python validate_shortcut.py <file.shortcut>
    python validate_shortcut.py --all   # validate all .shortcut files in current dir
"""

import plistlib
import sys
import os
import re
import json

# ============================================================
# KNOWN OUTPUT NAMES PER ACTION IDENTIFIER
# Collected from real Apple Shortcuts + drewocarr reference
# OutputName is primarily a display label - iOS tolerates variations
# but using the canonical name is safest.
# ============================================================
CANONICAL_OUTPUT_NAMES = {
    "is.workflow.actions.gettext":            "Text",
    "is.workflow.actions.text.replace":       "Replace Text",
    "is.workflow.actions.text.match":         "matches",
    "is.workflow.actions.text.changecase":    "Updated Text",
    "is.workflow.actions.text.split":         "Split Text",
    "is.workflow.actions.text.combine":       "Combined Text",
    "is.workflow.actions.detect.number":      "Number",
    "is.workflow.actions.number":             "Number",
    "is.workflow.actions.number.random":      "Random Number",
    "is.workflow.actions.math":              "Calculation Result",
    "is.workflow.actions.statistics":         "Statistics",
    "is.workflow.actions.count":              "Count",
    "is.workflow.actions.date":              "Current Date",  # also accepts "Date"
    "is.workflow.actions.format.date":        "Formatted Date",
    "is.workflow.actions.detect.date":        "Date",
    "is.workflow.actions.gettimebetweendates":"Time Between Dates",
    "is.workflow.actions.ask":               "Provided Input",
    "is.workflow.actions.askllm":            "Response",
    "is.workflow.actions.getvariable":       "Variable",
    "is.workflow.actions.setvariable":       None,  # no output
    "is.workflow.actions.appendvariable":    None,  # no output
    "is.workflow.actions.list":              "List",
    "is.workflow.actions.dictionary":        "Dictionary",
    "is.workflow.actions.getvalueforkey":    "Dictionary Value",
    "is.workflow.actions.setvalueforkey":    "Dictionary",
    "is.workflow.actions.url":               "URL",
    "is.workflow.actions.downloadurl":       "Contents of URL",
    "is.workflow.actions.getwebpagecontents":"Web Page Contents",
    "is.workflow.actions.urlencode":         "Encoded Text",
    "is.workflow.actions.url.expand":        "Expanded URL",
    "is.workflow.actions.url.getheaders":    "Headers of URL",
    "is.workflow.actions.getcurrentlocation":"Current Location",
    "is.workflow.actions.getmapslink":       "Maps Link",
    "is.workflow.actions.searchmaps":        None,  # no output
    "is.workflow.actions.notification":       None,  # no output
    "is.workflow.actions.showresult":         None,  # no output
    "is.workflow.actions.alert":             None,  # no output
    "is.workflow.actions.comment":           None,  # no output
    "is.workflow.actions.nothing":           "Nothing",
    "is.workflow.actions.detect.text":       "Text",
    "is.workflow.actions.detect.address":    "Addresses",
    "is.workflow.actions.detect.contacts":   "Contacts",
    "is.workflow.actions.detect.emailaddress":"Email Addresses",
    "is.workflow.actions.detect.link":       "URLs",
    "is.workflow.actions.detect.phonenumber":"Phone Numbers",
    "is.workflow.actions.detect.images":     "Images",
    "is.workflow.actions.detect.dictionary": "Dictionary",
    "is.workflow.actions.correctspelling":   "Corrected Text",
    "is.workflow.actions.hash":              "Hash",
    "is.workflow.actions.base64encode":      "Base64 Encoded",
    "is.workflow.actions.getitemname":       "Name",
    "is.workflow.actions.getitemtype":       "Type",
    "is.workflow.actions.setitemname":       "Renamed Item",
    "is.workflow.actions.getbatterylevel":   "Battery Level",
    "is.workflow.actions.getdevicedetails":  "Device Details",
    "is.workflow.actions.getipaddress":      "IP Address",
    "is.workflow.actions.getwifi":           "Wi-Fi Network",
    "is.workflow.actions.getclipboard":      "Clipboard",
    "is.workflow.actions.getarticle":        "Article",
    "is.workflow.actions.getrichtextfromhtml":"Rich Text from HTML",
    "is.workflow.actions.getrichtextfrommarkdown":"Rich Text from Markdown",
    "is.workflow.actions.getmarkdownfromrichtext":"Markdown from Rich Text",
    "is.workflow.actions.scanbarcode":       "QR/Barcode",
    "is.workflow.actions.getlastscreenshot": "Latest Screenshot",
    "is.workflow.actions.getlastvideo":      "Latest Video",
    "is.workflow.actions.getlatestbursts":   "Latest Bursts",
    "is.workflow.actions.getlatestlivephotos":"Latest Live Photos",
    "is.workflow.actions.getlatestphotoimport":"Latest Photo Import",
    "is.workflow.actions.getcurrentsong":    "Current Song",
    "is.workflow.actions.makezip":           "Archive",
    "is.workflow.actions.unzip":             "Files",
    "is.workflow.actions.documentpicker.open":"File",
    "is.workflow.actions.file.append":       None,  # no output
    "is.workflow.actions.file.getlink":      "File Link",
    "is.workflow.actions.previewdocument":   None,  # no output
    "is.workflow.actions.runsshscript":      "Shell Script Result",
    "is.workflow.actions.runjavascriptonwebpage":"JavaScript Result",
    "is.workflow.actions.runworkflow":       "Shortcut Result",
    "is.workflow.actions.getmyworkflows":    "My Shortcuts",
    "is.workflow.actions.openurl":           None,  # no output
    "is.workflow.actions.openapp":           None,  # no output
    "is.workflow.actions.speaktext":         None,  # no output
    "is.workflow.actions.print":             None,  # no output
    "is.workflow.actions.share":             None,  # no output
    "is.workflow.actions.exit":              None,  # no output
    "is.workflow.actions.delay":             None,  # no output
    "is.workflow.actions.waittoreturn":      None,  # no output
    "is.workflow.actions.vibrate":           None,  # no output
    "is.workflow.actions.flashlight":        None,  # no output
    # Repeat/conditional special cases
    "is.workflow.actions.repeat.count":      "Repeat Index",
    "is.workflow.actions.repeat.each":       "Repeat Item",
    "is.workflow.actions.conditional":       None,  # control flow
    "is.workflow.actions.choosefrommenu":    None,  # control flow
    # filter.photos
    "is.workflow.actions.filter.photos":     "Photos",
}

# Known aliases - some OutputNames are interchangeable
OUTPUT_NAME_ALIASES = {
    "is.workflow.actions.date": ["Current Date", "Date"],
}

# Valid magic variable types
VALID_MAGIC_TYPES = {
    "ActionOutput", "Variable", "CurrentDate", "Clipboard",
    "Ask", "ExtensionInput", "DeviceDetails", "ShortcutInput",
}

# Valid aggrandizement types
VALID_AGGRANDIZEMENT_TYPES = {
    "WFPropertyVariableAggrandizement",
    "WFDictionaryValueVariableAggrandizement",
    "WFCoercionVariableAggrandizement",
    "WFDateFormatVariableAggrandizement",
}

# Required top-level keys
REQUIRED_TOP_KEYS = {
    "WFWorkflowActions",
}

# Recommended top-level keys
RECOMMENDED_TOP_KEYS = {
    "WFWorkflowMinimumClientVersion",
    "WFWorkflowMinimumClientVersionString",
    "WFWorkflowClientVersion",
    "WFWorkflowIcon",
    "WFWorkflowName",
}


class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def add_info(self, msg):
        self.info.append(msg)

    @property
    def ok(self):
        return len(self.errors) == 0

    def report(self):
        lines = []
        if self.errors:
            lines.append(f"\n  ERRORS ({len(self.errors)}):")
            for e in self.errors:
                lines.append(f"    [ERROR] {e}")
        if self.warnings:
            lines.append(f"\n  WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                lines.append(f"    [WARN]  {w}")
        if self.info:
            lines.append(f"\n  INFO ({len(self.info)}):")
            for i in self.info:
                lines.append(f"    [INFO]  {i}")
        if not self.errors and not self.warnings:
            lines.append("\n  ALL CHECKS PASSED")
        return "\n".join(lines)


def validate_shortcut(filepath):
    """Validate a .shortcut file and return ValidationResult."""
    result = ValidationResult()
    filename = os.path.basename(filepath)

    # 1. Try to parse the plist
    try:
        with open(filepath, "rb") as f:
            data = plistlib.load(f)
    except plistlib.InvalidFileException:
        result.error(f"Cannot parse plist - file may be signed (Apple signing wrapper)")
        return result
    except Exception as e:
        result.error(f"Cannot read file: {e}")
        return result

    result.add_info(f"Plist parsed successfully")

    # 2. Check required top-level keys
    for key in REQUIRED_TOP_KEYS:
        if key not in data:
            result.error(f"Missing required top-level key: {key}")

    for key in RECOMMENDED_TOP_KEYS:
        if key not in data:
            result.warn(f"Missing recommended top-level key: {key}")

    if "WFWorkflowActions" not in data:
        return result

    actions = data["WFWorkflowActions"]
    result.add_info(f"Total actions: {len(actions)}")

    if data.get("WFWorkflowName"):
        result.add_info(f"Shortcut name: {data['WFWorkflowName']}")

    # 3. Build UUID -> action map (includes both UUID and GroupingIdentifier)
    uuid_to_action = {}
    uuid_to_index = {}
    grouping_to_action = {}  # GroupingIdentifier -> action (for Repeat Item refs)
    for i, action in enumerate(actions):
        params = action.get("WFWorkflowActionParameters", {})
        uid = params.get("UUID")
        if uid:
            uuid_to_action[uid] = action
            uuid_to_index[uid] = i
        # Repeat Each/Count use GroupingIdentifier as the UUID for "Repeat Item"
        gid = params.get("GroupingIdentifier")
        mode = params.get("WFControlFlowMode")
        if gid and mode == 0:  # start of loop
            grouping_to_action[gid] = action
            uuid_to_action[gid] = action
            uuid_to_index[gid] = i

    # 4. Validate each action
    grouping_ids = {}  # GroupingIdentifier -> list of (index, mode)

    for i, action in enumerate(actions):
        aid = action.get("WFWorkflowActionIdentifier", "")
        params = action.get("WFWorkflowActionParameters", {})

        if not aid:
            result.error(f"Action {i}: Missing WFWorkflowActionIdentifier")
            continue

        # Check action identifier format
        if not aid.startswith("is.workflow.actions.") and not aid.startswith("com."):
            result.warn(f"Action {i}: Unusual action identifier: {aid}")

        # Track control flow grouping
        gid = params.get("GroupingIdentifier")
        mode = params.get("WFControlFlowMode")
        if gid is not None:
            if gid not in grouping_ids:
                grouping_ids[gid] = []
            grouping_ids[gid].append((i, mode))

        # Validate all variable references in params
        _validate_references(params, i, aid, uuid_to_action, uuid_to_index, result)

    # 5. Validate control flow integrity
    for gid, entries in grouping_ids.items():
        modes = [m for _, m in entries]
        if 0 not in modes:
            result.error(f"Control flow group {gid[:8]}...: Missing start (WFControlFlowMode=0)")
        if 2 not in modes:
            result.error(f"Control flow group {gid[:8]}...: Missing end (WFControlFlowMode=2)")

    return result


def _validate_references(obj, action_idx, action_id, uuid_map, uuid_idx_map, result):
    """Recursively validate all variable references in an action's parameters."""
    if isinstance(obj, dict):
        # Check for WFTextTokenString
        if obj.get("WFSerializationType") == "WFTextTokenString":
            _validate_token_string(obj, action_idx, action_id, uuid_map, uuid_idx_map, result)

        # Check for WFTextTokenAttachment
        elif obj.get("WFSerializationType") == "WFTextTokenAttachment":
            value = obj.get("Value", {})
            _validate_single_attachment(value, action_idx, action_id, uuid_map, uuid_idx_map, result)

        else:
            for k, v in obj.items():
                _validate_references(v, action_idx, action_id, uuid_map, uuid_idx_map, result)

    elif isinstance(obj, list):
        for item in obj:
            _validate_references(item, action_idx, action_id, uuid_map, uuid_idx_map, result)


def _validate_token_string(obj, action_idx, action_id, uuid_map, uuid_idx_map, result):
    """Validate a WFTextTokenString structure."""
    value = obj.get("Value", {})
    string = value.get("string", "")
    attachments = value.get("attachmentsByRange", {})

    if not isinstance(string, str):
        result.error(f"Action {action_idx} ({action_id}): 'string' is not a string type")
        return

    # Count placeholder characters in the string
    placeholder_count = string.count("\ufffc")
    attachment_count = len(attachments)

    if placeholder_count != attachment_count:
        result.error(
            f"Action {action_idx} ({action_id}): "
            f"Placeholder count ({placeholder_count}) != attachment count ({attachment_count})"
        )

    # Validate each attachment position
    placeholder_positions = [m.start() for m in re.finditer("\ufffc", string)]

    for range_key, attachment in attachments.items():
        # Parse range key
        m = re.match(r"\{(\d+),\s*(\d+)\}", range_key)
        if not m:
            result.error(
                f"Action {action_idx} ({action_id}): "
                f"Invalid range key format: {range_key}"
            )
            continue

        pos = int(m.group(1))
        length = int(m.group(2))

        if length != 1:
            result.warn(
                f"Action {action_idx} ({action_id}): "
                f"Range length is {length}, expected 1 at {range_key}"
            )

        # Check position matches a placeholder
        if pos not in placeholder_positions:
            result.error(
                f"Action {action_idx} ({action_id}): "
                f"Range {range_key} points to position {pos} but no placeholder (U+FFFC) there. "
                f"Actual placeholder positions: {placeholder_positions}"
            )

        # Validate the attachment itself
        _validate_single_attachment(attachment, action_idx, action_id, uuid_map, uuid_idx_map, result)


def _validate_single_attachment(attachment, action_idx, action_id, uuid_map, uuid_idx_map, result):
    """Validate a single variable attachment reference."""
    if not isinstance(attachment, dict):
        return

    var_type = attachment.get("Type", "")

    # Validate type
    if var_type and var_type not in VALID_MAGIC_TYPES:
        result.warn(
            f"Action {action_idx} ({action_id}): "
            f"Unknown variable Type: {var_type}"
        )

    # Validate ActionOutput references
    if var_type == "ActionOutput":
        output_uuid = attachment.get("OutputUUID", "")
        output_name = attachment.get("OutputName", "")

        if not output_uuid:
            result.error(
                f"Action {action_idx} ({action_id}): "
                f"ActionOutput missing OutputUUID"
            )
        elif output_uuid not in uuid_map:
            result.error(
                f"Action {action_idx} ({action_id}): "
                f"OutputUUID {output_uuid[:8]}... references non-existent action"
            )
        else:
            # Check OutputName matches the source action
            source_action = uuid_map[output_uuid]
            source_id = source_action["WFWorkflowActionIdentifier"]
            source_idx = uuid_idx_map.get(output_uuid, "?")

            # Check if source action comes before this action
            if isinstance(source_idx, int) and source_idx >= action_idx:
                result.warn(
                    f"Action {action_idx} ({action_id}): "
                    f"References action {source_idx} ({source_id}) which is at same or later position"
                )

            # Check OutputName
            if source_id in CANONICAL_OUTPUT_NAMES:
                canonical = CANONICAL_OUTPUT_NAMES[source_id]
                if canonical is None:
                    result.warn(
                        f"Action {action_idx} ({action_id}): "
                        f"References output of {source_id} (action {source_idx}) "
                        f"which typically has no output"
                    )
                else:
                    aliases = OUTPUT_NAME_ALIASES.get(source_id, [canonical])
                    if output_name not in aliases and output_name != canonical:
                        result.warn(
                            f"Action {action_idx} ({action_id}): "
                            f"OutputName '{output_name}' for {source_id} "
                            f"- expected '{canonical}' (may still work as display label)"
                        )

        if not output_name:
            result.warn(
                f"Action {action_idx} ({action_id}): "
                f"ActionOutput missing OutputName (may cause display issues)"
            )

    # Validate Variable references
    elif var_type == "Variable":
        var_name = attachment.get("VariableName", "")
        if not var_name:
            result.warn(
                f"Action {action_idx} ({action_id}): "
                f"Variable type but no VariableName"
            )

    # Validate magic variables with aggrandizements
    if "Aggrandizements" in attachment:
        for aggr in attachment["Aggrandizements"]:
            aggr_type = aggr.get("Type", "")
            if aggr_type not in VALID_AGGRANDIZEMENT_TYPES:
                result.warn(
                    f"Action {action_idx} ({action_id}): "
                    f"Unknown aggrandizement type: {aggr_type}"
                )

            # Validate WFDateFormatVariableAggrandizement
            if aggr_type == "WFDateFormatVariableAggrandizement":
                style = aggr.get("WFDateFormatStyle", "")
                if style == "Custom" and not aggr.get("WFDateFormat"):
                    result.error(
                        f"Action {action_idx} ({action_id}): "
                        f"WFDateFormatVariableAggrandizement with Custom style but no WFDateFormat"
                    )
                if style not in ("Custom", "Short", "Medium", "Long", "Full", "Relative", ""):
                    result.warn(
                        f"Action {action_idx} ({action_id}): "
                        f"Unknown WFDateFormatStyle: {style}"
                    )

            # Validate WFPropertyVariableAggrandizement
            if aggr_type == "WFPropertyVariableAggrandizement":
                if not aggr.get("PropertyName"):
                    result.error(
                        f"Action {action_idx} ({action_id}): "
                        f"WFPropertyVariableAggrandizement missing PropertyName"
                    )

            # Validate WFDictionaryValueVariableAggrandizement
            if aggr_type == "WFDictionaryValueVariableAggrandizement":
                if not aggr.get("DictionaryKey"):
                    result.error(
                        f"Action {action_idx} ({action_id}): "
                        f"WFDictionaryValueVariableAggrandizement missing DictionaryKey"
                    )


def dump_shortcut(filepath):
    """Dump shortcut as readable JSON for debugging."""
    try:
        with open(filepath, "rb") as f:
            data = plistlib.load(f)
    except Exception as e:
        print(f"Cannot read: {e}")
        return

    def convert(obj):
        if isinstance(obj, bytes):
            return f"<{len(obj)} bytes>"
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert(i) for i in obj]
        return obj

    print(json.dumps(convert(data), indent=2, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--dump":
        if len(sys.argv) < 3:
            print("Usage: validate_shortcut.py --dump <file.shortcut>")
            sys.exit(1)
        dump_shortcut(sys.argv[2])
        sys.exit(0)

    if sys.argv[1] == "--all":
        files = sorted(f for f in os.listdir(".") if f.endswith(".shortcut"))
    else:
        files = sys.argv[1:]

    total_errors = 0
    total_warnings = 0

    for filepath in files:
        if not os.path.exists(filepath):
            print(f"\n{'='*60}")
            print(f"FILE: {filepath}")
            print(f"  [ERROR] File not found")
            total_errors += 1
            continue

        print(f"\n{'='*60}")
        print(f"FILE: {filepath}")

        result = validate_shortcut(filepath)
        print(result.report())

        total_errors += len(result.errors)
        total_warnings += len(result.warnings)

    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(files)} files, {total_errors} errors, {total_warnings} warnings")

    if total_errors > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
