import re
import html
from bs4 import BeautifulSoup
from utils.color import Logger
import logging


logging.basicConfig(level=logging.INFO, format="%(message)s")


class EmailPreprocessor(Logger):
    """Cleans and normalizes raw email bodies from n8n before AI processing."""

    name = "EmailPreprocessor"
    color = Logger.CYAN

    def _remove_html(self, text: str) -> str:
        before = len(text)
        text = html.unescape(text)
        try:
            text = BeautifulSoup(text, 'html.parser').get_text()
            self.log(f"HTML removed via BeautifulSoup ({before} → {len(text)} chars)")
        except Exception:
            text = re.sub(r'<[^>]+>', '', text)
            self.log(f"HTML removed via regex fallback ({before} → {len(text)} chars)")
        return text

    def _remove_special_characters(self, text: str) -> str:
        before = len(text)

        for char in ('\u200c', '\u200b', '\u200d', '\ufeff', '\u200e', '\u200f'):
            text = text.replace(char, '')

        text = text.replace('\xa0', ' ').replace('\u00a0', ' ')
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        self.log(f"Special chars normalized ({before} → {len(text)} chars)")
        return text

    def _remove_artifacts(self, text: str) -> str:
        before = len(text)

        text = re.sub(r'\[image:.*?\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[cid:.*?\]', '', text, flags=re.IGNORECASE)

        footer_patterns = [
            r'you received this (?:email|message).*?(?:\n|$)',
            r'unsubscribe.*?(?:\n|$)',
            r'copyright \d{4}.*?(?:\n|$)',
            r'this email was sent to.*?(?:\n|$)',
            r'if you no longer wish to receive.*?(?:\n|$)',
            r'view this email in your browser.*?(?:\n|$)',
            r'add us to your address book.*?(?:\n|$)',
            r'you are receiving this.*?(?:\n|$)',
        ]
        for pattern in footer_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        self.log(f"Artifacts/footers removed ({before} → {len(text)} chars)")
        return text

    def _remove_urls(self, text: str) -> str:
        before = len(text)
        text = re.sub(
            r'http[s]?://(?:[a-zA-Z0-9$\-_.+!*\'(),]|(?:%[0-9a-fA-F]{2}))+',
            '[LINK]',
            text
        )
        self.log(f"URLs masked ({before} → {len(text)} chars)")
        return text

    def _normalize(self, text: str) -> str:
        before_lines = len(text.split('\n'))
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        result = '\n'.join(lines).strip()
        self.log(f"Normalized lines ({before_lines} → {len(lines)} lines)")
        return result

    def clean(self, body: str | None) -> str | None:
        if not body:
            self.log("Skipped cleaning: body is empty")
            return None

        self.log(f"Starting clean pipeline ({len(body)} chars)")

        body = self._remove_html(body)
        body = self._remove_special_characters(body)
        body = self._remove_artifacts(body)
        body = self._remove_urls(body)
        body = self._normalize(body)

        self.log(f"Finished cleaning ({len(body)} chars)")
        return body or None
    

if __name__ == "__main__":
    from schemas import InboundEmail, InboundEmailBatch

    batch = InboundEmailBatch(
        total=3,
        lastEmailId="msg_003",
        emails=[
            InboundEmail(
                id="msg_001",
                threadId="thread_001",
                senderName="John Doe",
                senderEmail="john@example.com",
                subject="Project Update",
                date="2026-05-17",
                body="""
                    <html>
                        <body>
                            <h1>Project Update</h1>
                            <p>Hi team,&nbsp; hope you're doing well!</p>
                            <p>Here's the <a href="https://example.com/report">latest report</a>.</p>
                            <p>Please review by <strong>Friday</strong>.</p>
                            <br/>
                            <p>You received this email because you are subscribed.</p>
                            <p>Unsubscribe from this list.</p>
                        </body>
                    </html>
                """
            ),
            InboundEmail(
                id="msg_002",
                threadId="thread_002",
                senderName="Newsletter Bot",
                senderEmail="news@newsletter.com",
                subject="Your Weekly Digest",
                date="2026-05-17",
                body="Hey! \u200c \u200c \u200c \u200b Check out this week's top stories.\r\n\r\n\r\nStory 1: AI is changing everything https://somelink.com/story1\r\n\r\n\r\n\r\nStory 2: Markets are up https://somelink.com/story2\r\n\r\nCopyright 2026 Newsletter Inc.\r\nThis email was sent to you@example.com"
            ),
            InboundEmail(
                id="msg_003",
                threadId="thread_003",
                senderName=None,
                senderEmail="noreply@system.com",
                subject="Your invoice is ready",
                date="2026-05-17",
                body=None
            )
        ]
    )

    preprocessor = EmailPreprocessor()

    print("=" * 60)
    for email in batch.emails:
        cleaned = preprocessor.clean(email.body)
        print(f"ID      : {email.id}")
        print(f"From    : {email.sender_name or 'Unknown'} <{email.sender_email}>")
        print(f"Subject : {email.subject}")
        print(f"Body    :\n{cleaned}")
        print("=" * 60)