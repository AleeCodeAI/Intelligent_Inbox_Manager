from typing import Optional

APPOINTMENT_CONFIRMATION_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
</head>
<body style="margin:0;padding:0;background:#0d1b2a;font-family:'DM Sans',Arial,sans-serif;">

  <table role="presentation" style="width:100%;border-collapse:collapse;background:#0d1b2a;">
    <tr>
      <td style="padding:48px 24px;">
        <table role="presentation" style="width:100%;max-width:580px;margin:0 auto;border-collapse:collapse;background:#ffffff;border-radius:12px;overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="background:#122d4b;padding:28px 40px 24px;">
              <p style="margin:0 0 6px 0;font-family:'DM Sans',Arial,sans-serif;font-size:11px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:#7fa8c9;">
                Appointment confirmed
              </p>
              <h1 style="margin:0;font-family:'Lora',Georgia,serif;font-size:22px;font-weight:600;color:#e8f0f7;line-height:1.3;">
                Your meeting is scheduled
              </h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 40px;">

              <p style="margin:0 0 20px 0;font-family:'Lora',Georgia,serif;font-size:17px;line-height:1.6;color:#1a2a3a;font-style:italic;">
                Dear {recipient_name},
              </p>

              <p style="margin:0 0 24px 0;font-family:'DM Sans',Arial,sans-serif;font-size:15px;line-height:1.75;color:#2c3e50;">
                This is a confirmation that your appointment has been scheduled. Here are the details:
              </p>

              <!-- Details card -->
              <table role="presentation" style="width:100%;border-collapse:collapse;background:#f4f7fa;border-radius:8px;margin:0 0 24px 0;">
                <tr>
                  <td style="padding:20px 24px;">

                    <table role="presentation" style="width:100%;border-collapse:collapse;">
                      <tr>
                        <td style="padding:0 0 14px 0;">
                          <p style="margin:0 0 4px 0;font-family:'DM Sans',Arial,sans-serif;font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#7fa8c9;">Title</p>
                          <p style="margin:0;font-family:'DM Sans',Arial,sans-serif;font-size:15px;font-weight:600;color:#122d4b;">{title}</p>
                        </td>
                      </tr>
                      <tr>
                        <td style="border-top:1px solid #dde6ef;padding:14px 0 14px 0;">
                          <p style="margin:0 0 4px 0;font-family:'DM Sans',Arial,sans-serif;font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#7fa8c9;">Starts</p>
                          <p style="margin:0;font-family:'DM Sans',Arial,sans-serif;font-size:15px;font-weight:600;color:#122d4b;">{start}</p>
                        </td>
                      </tr>
                      <tr>
                        <td style="border-top:1px solid #dde6ef;padding:14px 0 0 0;">
                          <p style="margin:0 0 4px 0;font-family:'DM Sans',Arial,sans-serif;font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#7fa8c9;">Ends</p>
                          <p style="margin:0;font-family:'DM Sans',Arial,sans-serif;font-size:15px;font-weight:600;color:#122d4b;">{end}</p>
                        </td>
                      </tr>
                    </table>

                  </td>
                </tr>
              </table>

              <p style="margin:0 0 22px 0;font-family:'DM Sans',Arial,sans-serif;font-size:15px;line-height:1.75;color:#2c3e50;">
                Please ensure you are available at the scheduled time. If you need to reschedule or have any questions, don't hesitate to reach out.
              </p>

              <!-- Divider -->
              <table role="presentation" style="width:100%;border-collapse:collapse;margin:28px 0;">
                <tr><td style="border-top:1px solid #e4eaf0;font-size:0;">&nbsp;</td></tr>
              </table>

              <!-- Signature -->
              <p style="margin:0 0 2px 0;font-family:'Lora',Georgia,serif;font-size:17px;font-weight:600;color:#122d4b;">
                Alee
              </p>
              <p style="margin:0;font-family:'DM Sans',Arial,sans-serif;font-size:13px;font-weight:500;letter-spacing:0.04em;color:#7fa8c9;">
                Applied AI Engineer
              </p>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f4f7fa;padding:14px 40px;">
              <p style="margin:0;font-family:'DM Sans',Arial,sans-serif;font-size:12px;color:#8fa3b5;letter-spacing:0.03em;">
                &#9679;&nbsp;&nbsp;Sent with care &middot; Confidential
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""


def render_appointment_confirmation(
    recipient_name: Optional[str],
    title: str,
    start: str,
    end: str,
) -> str:
    name = recipient_name or "there"
    return APPOINTMENT_CONFIRMATION_TEMPLATE.format(
        recipient_name=name,
        title=title,
        start=start,
        end=end,
    )