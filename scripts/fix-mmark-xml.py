#!/usr/bin/env python3
"""Post-process mmark XML for idnits and RFC 7991 compliance.

mmark v2 wraps normative and informative reference sections in an outer
<references><name>References</name> element. idnits rejects that wrapper;
only Normative References and Informative References are valid section names.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def fix_submission_type(text: str) -> str:
    """Drop submissionType on individual I-Ds without a declared stream.

    mmark defaults submissionType to IETF, but Datatracker records -00
    submissions with no stream until a working group adopts the draft.
    idnits flags submissionType="IETF" against that state (SUBMISSION_TYPE_UNEXPECTED).
    """
    if re.search(r'<seriesInfo[^>]*\bstream="IETF"', text):
        return text
    return re.sub(r' submissionType="IETF"', "", text, count=1)


def fix_references_wrapper(text: str) -> str:
    open_tag = "<references><name>References</name>\n"
    if open_tag not in text:
        return text
    text = text.replace(open_tag, "", 1)
    text, n = re.subn(
        r"</references>\n</references>\n(\n)(?=</back>|<section)",
        r"</references>\n\1",
        text,
        count=1,
    )
    if n != 1:
        text, n = re.subn(
            r"</references>\n</references>\n\n</back>",
            "</references>\n\n</back>",
            text,
            count=1,
        )
    if n != 1:
        raise SystemExit(
            "fix-mmark-xml: expected double </references> before </back>; "
            "mmark output format may have changed"
        )
    return text


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} <draft.xml>")
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    text = fix_references_wrapper(text)
    text = fix_submission_type(text)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
