// Test sample #2: Notification system — targets general SKILL.md principles
// Focuses on: OCP, LSP, ISP, Testability, Clean Code, Architecture, FP, Security

import { Request, Response } from "express";

// ─── Architecture: Layer violation ───────────────────────────────────
// [ISSUE: Domain logic importing HTTP/infrastructure concerns directly]
import axios from "axios";
import * as fs from "fs";

// ─── ISP: Fat interface ─────────────────────────────────────────────
// [ISSUE: Interface too broad — forces implementors to stub methods they don't need]
interface INotificationChannel {
  sendEmail(to: string, subject: string, body: string): Promise<void>;
  sendSMS(phone: string, message: string): Promise<void>;
  sendPush(deviceToken: string, payload: object): Promise<void>;
  sendSlack(channel: string, message: string): Promise<void>;
  getDeliveryStatus(id: string): Promise<string>;
  retryFailed(): Promise<number>;
  generateReport(): Promise<string>;
}

// ─── LSP: Subtype contract violation ────────────────────────────────
interface Shape {
  area(): number; // Contract: returns a non-negative number
}

class Rectangle implements Shape {
  constructor(protected width: number, protected height: number) {}
  area(): number {
    return this.width * this.height;
  }
}

// [ISSUE: LSP violation — Square overrides setters in a way that breaks Rectangle's contract]
// Callers expecting independent width/height will get unexpected behavior
class Square extends Rectangle {
  constructor(side: number) {
    super(side, side);
  }
  // [ISSUE: Overriding width silently changes height — violates substitutability]
  set widthValue(w: number) {
    this.width = w;
    this.height = w;
  }
  set heightValue(h: number) {
    this.width = h;
    this.height = h;
  }
}

// ─── OCP: Switch that must grow ─────────────────────────────────────
type NotificationType = "email" | "sms" | "push" | "slack";

// [ISSUE: OCP violation — adding a new notification type requires modifying this function]
function sendNotification(type: NotificationType, recipient: string, message: string) {
  // [ISSUE: Deep nesting — 3+ levels]
  if (type === "email") {
    if (recipient.includes("@")) {
      if (message.length > 0) {
        // [ISSUE: Hardcoded dependency — direct axios call, not injectable]
        axios.post("https://email-api.internal/send", {
          to: recipient,
          body: message,
        });
      }
    }
  } else if (type === "sms") {
    if (recipient.match(/^\+?[0-9]{10,15}$/)) {
      if (message.length <= 160) {
        axios.post("https://sms-api.internal/send", {
          phone: recipient,
          text: message,
        });
      } else {
        // [ISSUE: Code duplication — same splitting logic could be extracted]
        const parts = [];
        for (let i = 0; i < message.length; i += 160) {
          parts.push(message.slice(i, i + 160));
        }
        for (const part of parts) {
          axios.post("https://sms-api.internal/send", {
            phone: recipient,
            text: part,
          });
        }
      }
    }
  } else if (type === "push") {
    axios.post("https://push-api.internal/send", {
      token: recipient,
      payload: { message },
    });
  } else if (type === "slack") {
    axios.post("https://slack-api.internal/send", {
      channel: recipient,
      text: message,
    });
  }
  // [ISSUE: No return value, no error handling — fire and forget with no feedback]
}

// ─── FP: Hidden side effects ────────────────────────────────────────
// [ISSUE: Function named "calculate" but has side effects — logs, writes file, sends HTTP]
function calculateNotificationStats(notifications: Array<{ type: string; sentAt: Date }>) {
  let emailCount = 0;
  let smsCount = 0;

  for (const n of notifications) {
    if (n.type === "email") emailCount++;
    if (n.type === "sms") smsCount++;
  }

  // [ISSUE: Side effect hidden in a "calculate" function]
  console.log(`Stats: ${emailCount} emails, ${smsCount} sms`);
  fs.writeFileSync("/tmp/notification-stats.json", JSON.stringify({ emailCount, smsCount }));
  axios.post("https://analytics.internal/track", { emailCount, smsCount });

  return { emailCount, smsCount };
}

// ─── Testability: Hard-coded dependencies + non-deterministic ───────
class NotificationScheduler {
  // [ISSUE: Non-deterministic — uses Date.now() directly, not injectable]
  shouldSendNow(scheduledAt: number): boolean {
    return Date.now() >= scheduledAt;
  }

  // [ISSUE: Hard-coded file system dependency — cannot test without real FS]
  loadTemplate(name: string): string {
    return fs.readFileSync(`/etc/templates/${name}.html`, "utf-8");
  }

  // [ISSUE: Complex method mixing abstraction levels — scheduling, template loading, sending]
  async processScheduled(): Promise<void> {
    const pending = JSON.parse(fs.readFileSync("/var/data/pending.json", "utf-8"));
    for (const item of pending) {
      if (this.shouldSendNow(item.scheduledAt)) {
        const tmpl = this.loadTemplate(item.template);
        // [ISSUE: Dead code — variable assigned but never used]
        const debugInfo = `Processing ${item.id} at ${new Date().toISOString()}`;
        const content = tmpl.replace("{{message}}", item.message);
        sendNotification(item.type, item.recipient, content);
      }
    }
  }
}

// ─── Clean Code: Bad naming + duplication ───────────────────────────
// [ISSUE: Non-descriptive names — what does "d" mean? "temp"? "x"?]
function processData(d: any[]) {
  const temp: any[] = [];
  for (let x = 0; x < d.length; x++) {
    // [ISSUE: Duplicated validation logic — same email check as line 67]
    if (d[x].recipient && d[x].recipient.includes("@")) {
      temp.push(d[x]);
    }
  }
  return temp;
}

// [ISSUE: Dead code — function is never called anywhere]
function legacyNotify(email: string, msg: string) {
  // Old implementation kept "just in case"
  return axios.post("https://old-email-service.internal/send", { email, msg });
}

// ─── Security: XSS + missing auth ──────────────────────────────────
// [ISSUE: No authentication/authorization middleware on this route]
function handlePreview(req: Request, res: Response) {
  const template = req.query.template as string;

  // [ISSUE: Path traversal — user controls file path without sanitization]
  const content = fs.readFileSync(`/etc/templates/${template}`, "utf-8");

  // [ISSUE: XSS — user input rendered directly into HTML without escaping]
  const rendered = content.replace("{{name}}", req.query.name as string);
  res.send(`<html><body>${rendered}</body></html>`);
}

// ─── Architecture: Anemic domain model ──────────────────────────────
// [ISSUE: Entity is a pure data bag — all logic lives in service functions above]
class Notification {
  id: string = "";
  type: string = "";        // [ISSUE: string instead of NotificationType union]
  recipient: string = "";
  message: string = "";
  scheduledAt: number = 0;
  sentAt: Date | null = null;
  status: string = "";       // [ISSUE: string instead of union/enum]
}
