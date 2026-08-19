<?php
class EmailSender {
    private string $to;
    private string $subject;
    private string $body;
    private string $headers = '';

    public function __construct(string $to, string $subject) {
        $this->to = $to;
        $this->subject = $subject;
    }

    public function setFrom(string $email, string $name = ''): self {
        $this->headers .= "From: " . ($name ? "$name <{$email}>" : $email) . "\r\n";
        return $this;
    }

    public function setReplyTo(string $email, string $name = ''): self {
        $this->headers .= "Reply-To: " . ($name ? "$name <{$email}>" : $email) . "\r\n";
        return $this;
    }

    public function setHTML(string $body): self {
        $this->body = $body;
        $this->headers .= "MIME-Version: 1.0\r\n";
        $this->headers .= "Content-Type: text/html; charset=UTF-8\r\n";
        return $this;
    }

    public function setText(string $body): self {
        $this->body = $body;
        $this->headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
        return $this;
    }

    public function send(): bool {
        return mail($this->to, $this->subject, $this->body, $this->headers);
    }

    public static function sendContactEmail(array $data): bool {
        $email = new self(CONTACT_EMAIL, 'New Contact: ' . sanitize($data['subject'] ?? 'General Inquiry'));
        $email->setFrom(sanitize($data['email']), sanitize($data['firstName'] . ' ' . $data['lastName']));
        $email->setReplyTo(sanitize($data['email']), sanitize($data['firstName']));
        
        $html = '<!DOCTYPE html><html><head><style>body{font-family:Arial,sans-serif;color:#333;}h2{color:#0d1b2a;}.field{margin:10px 0;}.label{font-weight:bold;color:#6b7280;}</style></head><body>';
        $html .= '<h2>New Contact Message</h2>';
        $html .= '<div class="field"><span class="label">Name:</span> ' . sanitize($data['firstName'] . ' ' . $data['lastName']) . '</div>';
        $html .= '<div class="field"><span class="label">Email:</span> ' . sanitize($data['email']) . '</div>';
        $html .= '<div class="field"><span class="label">Interest:</span> ' . sanitize($data['interest'] ?? 'Not specified') . '</div>';
        $html .= '<div class="field"><span class="label">Message:</span><br>' . nl2br(sanitize($data['message'])) . '</div>';
        $html .= '<hr><p style="color:#6b7280;font-size:12px;">Sent from ' . SITE_NAME . ' contact form</p>';
        $html .= '</body></html>';

        $email->setHTML($html);
        return $email->send();
    }

    public static function sendWaitlistConfirmation(string $email): bool {
        $mailer = new self($email, 'Welcome to the Britlearn App Waitlist!');
        $mailer->setFrom(CONTACT_EMAIL, SITE_NAME);
        
        $html = '<!DOCTYPE html><html><head><style>body{font-family:Arial,sans-serif;color:#333;text-align:center;}h2{color:#0d1b2a;}.highlight{color:#2563eb;}</style></head><body>';
        $html .= '<h2>Welcome to the Waitlist!</h2>';
        $html .= '<p>Thank you for joining the <span class="highlight">Britlearn App</span> waitlist.</p>';
        $html .= '<p>We\'ll notify you as soon as the app is ready to launch in 2026.</p>';
        $html .= '<p>In the meantime, explore our courses at <a href="' . SITE_URL . '">' . SITE_NAME . '</a></p>';
        $html .= '<hr><p style="color:#6b7280;font-size:12px;">' . SITE_NAME . ' · London, United Kingdom</p>';
        $html .= '</body></html>';

        $mailer->setHTML($html);
        return $mailer->send();
    }
}
