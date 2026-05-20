HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#ffffff;">
  <table role="presentation" style="width:100%;border-collapse:collapse;">
    <tr>
      <td style="padding:28px 32px;">

        <p style="margin:0 0 18px 0;font-size:16px;line-height:1.6;color:#333333;">
          Dear {recipient_name},
        </p>

        {body_paragraphs}

        <p style="margin:24px 0 0 0;font-size:16px;line-height:1.6;color:#333333;">
          Best regards,<br>
          <strong>Alee</strong><br>
          <span style="color:#888888;font-size:14px;">Applied AI Engineer</span>
        </p>

      </td>
    </tr>
  </table>
</body>
</html>
"""

_PARAGRAPH = (
    '<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#333333;">'
    "{text}"
    "</p>"
)


def _to_paragraphs(plain_text: str) -> str:
    """Convert plain text (newline-separated) into HTML <p> blocks."""
    paragraphs = [p.strip() for p in plain_text.strip().split("\n\n") if p.strip()]
    return "\n        ".join(_PARAGRAPH.format(text=p) for p in paragraphs)


def render_email(recipient_name: str | None, body: str) -> str:
    name = recipient_name or "there"
    return HTML_TEMPLATE.format(
        recipient_name=name,
        body_paragraphs=_to_paragraphs(body),
    )HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#ffffff;">
  <table role="presentation" style="width:100%;border-collapse:collapse;">
    <tr>
      <td style="padding:28px 32px;">

        <p style="margin:0 0 18px 0;font-size:16px;line-height:1.6;color:#333333;">
          Dear {recipient_name},
        </p>

        {body_paragraphs}

        <p style="margin:24px 0 0 0;font-size:16px;line-height:1.6;color:#333333;">
          Best regards,<br>
          <strong>Alee</strong><br>
          <span style="color:#888888;font-size:14px;">Applied AI Engineer</span>
        </p>

      </td>
    </tr>
  </table>
</body>
</html>
"""

_PARAGRAPH = (
    '<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#333333;">'
    "{text}"
    "</p>"
)


def _to_paragraphs(plain_text: str) -> str:
    """Convert plain text (newline-separated) into HTML <p> blocks."""
    paragraphs = [p.strip() for p in plain_text.strip().split("\n\n") if p.strip()]
    return "\n        ".join(_PARAGRAPH.format(text=p) for p in paragraphs)


def render_email(recipient_name: str | None, body: str) -> str:
    name = recipient_name or "there"
    return HTML_TEMPLATE.format(
        recipient_name=name,
        body_paragraphs=_to_paragraphs(body),
    )